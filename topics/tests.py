from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from PeopleFind.testing import make_interest, make_user
from topics.models import Comment, Topic
from topics.utils import slug_generator, transliterate
from users.models import UserRoles


class SlugTests(TestCase):
    def setUp(self):
        self.author = make_user(1)
        self.interest = make_interest('Игры', self.author)

    def create_topic(self, title):
        return Topic.objects.create(title=title, description='x', author=self.author, interest=self.interest)

    def test_transliterate(self):
        self.assertEqual(transliterate('Привет, Мир!'), 'privet, mir!')
        self.assertEqual(transliterate('Щука и ёж'), 'shchuka i ezh')

    def test_cyrillic_title_gets_readable_slug(self):
        """Регрессия: slugify('Привет') == '', а пустой slug не подходит под <slug:slug>."""
        topic = self.create_topic('Привет мир')
        self.assertEqual(topic.slug, 'privet-mir')

    def test_same_title_gets_unique_slug(self):
        first = self.create_topic('Привет мир')
        second = self.create_topic('Привет мир')
        self.assertNotEqual(first.slug, second.slug)
        self.assertTrue(second.slug.startswith('privet-mir-'))

    def test_title_without_letters_gets_fallback_slug(self):
        self.assertEqual(self.create_topic('!!!').slug, 'topic')

    def test_slug_generator_ignores_the_instance_itself(self):
        topic = self.create_topic('Привет мир')
        self.assertEqual(slug_generator(topic), 'privet-mir')

    def test_topic_url_can_be_reversed_for_cyrillic_title(self):
        topic = self.create_topic('Привет мир')
        url = reverse('topics:detail', kwargs={'pk': self.interest.pk, 'slug': topic.slug})
        self.assertEqual(self.client.get(url).status_code, 200)


class CommentModelTests(TestCase):
    def setUp(self):
        self.user = make_user(1)
        self.interest = make_interest('Игры', self.user)
        self.topic = Topic.objects.create(title='T', author=self.user, interest=self.interest)

    def test_comment_needs_exactly_one_target(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Comment.objects.create(user=self.user, text='x', interest=self.interest, topic=self.topic)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Comment.objects.create(user=self.user, text='x')
        Comment.objects.create(user=self.user, text='x', interest=self.interest)
        Comment.objects.create(user=self.user, text='x', topic=self.topic)


class CommentCreateViewTests(TestCase):
    def setUp(self):
        self.user = make_user(1)
        self.interest = make_interest('Игры', self.user)
        self.topic = Topic.objects.create(title='T', author=self.user, interest=self.interest)
        self.url = reverse('topics:new-comment')
        self.client.force_login(self.user)

    def test_comment_on_interest(self):
        response = self.client.post(self.url, {'text': ' Привет ', 'interest': self.interest.pk, 'topic': ''})
        self.assertEqual(response.json(), {'success': True})
        comment = Comment.objects.get()
        self.assertEqual((comment.text, comment.interest, comment.topic), ('Привет', self.interest, None))

    def test_comment_on_topic(self):
        self.client.post(self.url, {'text': 'Привет', 'interest': '', 'topic': self.topic.pk})
        comment = Comment.objects.get()
        self.assertEqual((comment.interest, comment.topic), (None, self.topic))

    def test_empty_text_is_rejected(self):
        response = self.client.post(self.url, {'text': '   ', 'interest': self.interest.pk})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Comment.objects.exists())

    def test_too_long_text_is_rejected(self):
        response = self.client.post(self.url, {'text': 'a' * 2001, 'interest': self.interest.pk})
        self.assertEqual(response.status_code, 400)

    def test_exactly_one_target_is_required(self):
        both = self.client.post(self.url, {'text': 'x', 'interest': self.interest.pk, 'topic': self.topic.pk})
        neither = self.client.post(self.url, {'text': 'x'})
        self.assertEqual((both.status_code, neither.status_code), (400, 400))

    def test_unknown_target_is_404(self):
        self.assertEqual(self.client.post(self.url, {'text': 'x', 'interest': 9999}).status_code, 404)

    def test_requires_login(self):
        self.client.logout()
        self.assertEqual(self.client.post(self.url, {'text': 'x', 'interest': self.interest.pk}).status_code, 302)


class DeleteObjectViewTests(TestCase):
    """Регрессия: 'user is comment.user' всегда было False, автор не мог удалить свое."""

    def setUp(self):
        self.author = make_user(1)
        self.stranger = make_user(2)
        self.moderator = make_user(3, role=UserRoles.MODERATOR)
        self.interest = make_interest('Игры', self.author)
        self.topic = Topic.objects.create(title='T', author=self.author, interest=self.interest)
        self.comment = Comment.objects.create(user=self.author, text='x', topic=self.topic)
        self.url = reverse('topics:delete')

    def test_author_can_delete_own_comment(self):
        self.client.force_login(self.author)
        self.assertEqual(self.client.post(self.url, {'comment': self.comment.pk}).json(), {'success': True})
        self.assertFalse(Comment.objects.exists())

    def test_author_can_delete_own_topic(self):
        self.client.force_login(self.author)
        self.assertEqual(self.client.post(self.url, {'topic': self.topic.pk}).status_code, 200)
        self.assertFalse(Topic.objects.exists())

    def test_stranger_cannot_delete(self):
        self.client.force_login(self.stranger)
        self.assertEqual(self.client.post(self.url, {'comment': self.comment.pk}).status_code, 403)
        self.assertEqual(self.client.post(self.url, {'topic': self.topic.pk}).status_code, 403)
        self.assertTrue(Comment.objects.exists() and Topic.objects.exists())

    def test_moderator_can_delete_anything(self):
        self.client.force_login(self.moderator)
        self.assertEqual(self.client.post(self.url, {'comment': self.comment.pk}).status_code, 200)

    def test_missing_or_bad_ids(self):
        self.client.force_login(self.author)
        self.assertEqual(self.client.post(self.url).status_code, 400)
        self.assertEqual(self.client.post(self.url, {'comment': 'abc'}).status_code, 400)
        self.assertEqual(self.client.post(self.url, {'comment': 9999}).status_code, 404)

    def test_requires_login(self):
        self.assertEqual(self.client.post(self.url, {'comment': self.comment.pk}).status_code, 302)


class TopicPagesTests(TestCase):
    def setUp(self):
        self.author = make_user(1)
        self.interest = make_interest('Игры', self.author)
        self.other_interest = make_interest('Музыка')
        self.topic = Topic.objects.create(title='Привет мир', description='Текст', author=self.author,
                                          interest=self.interest)

    def test_topic_must_belong_to_interest_in_url(self):
        url = reverse('topics:detail', kwargs={'pk': self.other_interest.pk, 'slug': self.topic.slug})
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_topic_list_for_unknown_interest_is_404(self):
        self.assertEqual(self.client.get(reverse('topics:list', kwargs={'pk': 9999})).status_code, 404)

    def test_empty_topic_list_message(self):
        response = self.client.get(reverse('topics:list', kwargs={'pk': self.other_interest.pk}))
        self.assertContains(response, 'Нет топиков')

    def test_pages_work_after_topic_author_is_deleted(self):
        """Регрессия: author=SET_NULL, а шаблон делал {% url ... object.author.slug %}."""
        self.author.delete()
        self.topic.refresh_from_db()
        self.assertIsNone(self.topic.author)
        detail = reverse('topics:detail', kwargs={'pk': self.interest.pk, 'slug': self.topic.slug})
        for url in (detail, reverse('topics:list', kwargs={'pk': self.interest.pk}),
                    reverse('interests:detail', kwargs={'pk': self.interest.pk}), reverse('users:index')):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
        self.assertContains(self.client.get(detail), 'Удаленный пользователь')

    def test_create_topic_sets_author_and_interest(self):
        reader = make_user(5)
        self.client.force_login(reader)
        response = self.client.post(reverse('topics:create', kwargs={'pk': self.interest.pk}),
                                    {'title': 'Новый топик', 'description': 'Описание'})
        self.assertEqual(response.status_code, 302)
        topic = Topic.objects.get(title='Новый топик')
        self.assertEqual((topic.author, topic.interest), (reader, self.interest))
        self.assertEqual(Topic.objects.filter(title='Новый топик').count(), 1)
