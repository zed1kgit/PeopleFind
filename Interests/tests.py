from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from Interests.models import Interest
from Interests.utils import find_people, find_similar_users
from PeopleFind.testing import make_interest, make_user
from topics.models import Comment, Topic
from users.models import UserRoles


class FindSimilarUsersTests(TestCase):
    def setUp(self):
        self.me = make_user(1)
        self.games = make_interest('Игры', self.me)
        self.music = make_interest('Музыка', self.me)
        self.cinema = make_interest('Кино')

        self.both = make_user(2)
        self.games.members.add(self.both)
        self.music.members.add(self.both)
        self.one = make_user(3)
        self.games.members.add(self.one)
        self.other = make_user(4)
        self.cinema.members.add(self.other)

    def test_orders_by_number_of_common_interests(self):
        result = find_similar_users(self.me)
        self.assertEqual([u.pk for u in result], [self.both.pk, self.one.pk])
        self.assertEqual(result[0].common_interests_count, 2)
        self.assertEqual(result[1].common_interests_count, 1)

    def test_excludes_already_rated_users(self):
        self.me.denied_users.add(self.both)
        self.me.approved_users.add(self.one)
        self.assertEqual(find_similar_users(self.me), [])

    def test_excludes_inactive_and_unverified_users(self):
        inactive = make_user(5, is_active=False)
        unverified = make_user(6, is_email_verified=False)
        self.games.members.add(inactive, unverified)
        self.assertNotIn(inactive, find_similar_users(self.me))
        self.assertNotIn(unverified, find_similar_users(self.me))

    def test_user_without_interests_finds_nobody(self):
        lonely = make_user(7)
        self.assertEqual(find_similar_users(lonely), [])
        self.assertIsNone(find_people(lonely))

    def test_find_people_returns_a_candidate(self):
        self.assertIn(find_people(self.me), (self.both, self.one))

    def test_limit_is_applied(self):
        self.assertEqual(len(find_similar_users(self.me, limit=1)), 1)


class PeopleSearchViewsTests(TestCase):
    def setUp(self):
        self.me = make_user(1)
        self.friend = make_user(2, name='Friend')
        make_interest('Игры', self.me, self.friend)
        self.client.force_login(self.me)

    def test_search_page_shows_candidate(self):
        response = self.client.get(reverse('interests:user-found'))
        self.assertContains(response, 'Friend')

    def test_search_page_without_candidates(self):
        self.me.denied_users.add(self.friend)
        response = self.client.get(reverse('interests:user-found'))
        self.assertContains(response, 'Не найдено похожих пользователей')

    def test_search_requires_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('interests:user-found')).status_code, 302)

    def test_approve_adds_user_and_reports_no_more_candidates(self):
        response = self.client.post(reverse('interests:approve-user'), {'user-id': self.friend.pk})
        self.assertEqual(response.json()['new_object_id'], 'none')
        self.assertIn(self.friend, self.me.approved_users.all())

    def test_deny_adds_to_denied_and_returns_next_candidate(self):
        third = make_user(3)
        Interest.objects.get(name='Игры').members.add(third)
        response = self.client.post(reverse('interests:deny-user'), {'user-id': self.friend.pk})
        data = response.json()
        self.assertEqual(data['new_object_id'], third.pk)
        self.assertIn('new_object', data)
        self.assertIn(self.friend, self.me.denied_users.all())

    def test_cannot_rate_yourself(self):
        self.client.post(reverse('interests:approve-user'), {'user-id': self.me.pk})
        self.assertFalse(self.me.approved_users.exists())

    def test_bad_user_id_is_404(self):
        self.assertEqual(self.client.post(reverse('interests:approve-user'), {'user-id': 'abc'}).status_code, 404)
        self.assertEqual(self.client.post(reverse('interests:approve-user'), {'user-id': 9999}).status_code, 404)
        self.assertEqual(self.client.post(reverse('interests:approve-user')).status_code, 404)

    def test_rating_requires_post(self):
        self.assertEqual(self.client.get(reverse('interests:approve-user')).status_code, 405)


class ToggleInterestTests(TestCase):
    def setUp(self):
        self.user = make_user(1)
        self.interest = make_interest('Игры')
        self.url = reverse('interests:toggle-interest', kwargs={'pk': self.interest.pk})

    def test_subscribe_and_unsubscribe(self):
        self.client.force_login(self.user)
        data = self.client.post(self.url).json()
        self.assertEqual((data['subscribed'], data['members_count']), (True, 1))
        data = self.client.post(self.url).json()
        self.assertEqual((data['subscribed'], data['members_count']), (False, 0))

    def test_unknown_interest_is_404(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(reverse('interests:toggle-interest', kwargs={'pk': 9999})).status_code, 404)

    def test_requires_login(self):
        self.assertEqual(self.client.post(self.url).status_code, 302)


class InterestPermissionsTests(TestCase):
    def setUp(self):
        self.interest = make_interest('Игры')

    def test_regular_user_cannot_manage_interests(self):
        self.client.force_login(make_user(1))
        self.assertEqual(self.client.get(reverse('interests:create')).status_code, 403)
        self.assertEqual(self.client.get(reverse('interests:update', kwargs={'pk': self.interest.pk})).status_code, 403)
        self.assertEqual(self.client.get(reverse('interests:delete', kwargs={'pk': self.interest.pk})).status_code, 403)

    def test_anonymous_gets_403(self):
        self.assertEqual(self.client.get(reverse('interests:create')).status_code, 403)

    def test_moderator_can_create_and_update_but_not_delete(self):
        self.client.force_login(make_user(1, role=UserRoles.MODERATOR))
        self.assertEqual(self.client.get(reverse('interests:create')).status_code, 200)
        self.assertEqual(self.client.get(reverse('interests:update', kwargs={'pk': self.interest.pk})).status_code, 200)
        self.assertEqual(self.client.get(reverse('interests:delete', kwargs={'pk': self.interest.pk})).status_code, 403)

    def test_admin_can_delete(self):
        self.client.force_login(make_user(1, role=UserRoles.ADMIN))
        response = self.client.post(reverse('interests:delete', kwargs={'pk': self.interest.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Interest.objects.filter(pk=self.interest.pk).exists())

    def test_create_form_accepts_logo_upload_enctype(self):
        self.client.force_login(make_user(1, role=UserRoles.MODERATOR))
        response = self.client.get(reverse('interests:create'))
        self.assertContains(response, 'multipart/form-data')


class InterestPagesRenderTests(TestCase):
    """Дымовые тесты: страницы раздела должны рендериться для гостя и пользователя."""

    def setUp(self):
        self.author = make_user(1)
        self.reader = make_user(2)
        self.interest = make_interest('Игры', self.author)
        self.topic = Topic.objects.create(title='Привет мир', description='Текст', author=self.author,
                                          interest=self.interest)
        Comment.objects.create(user=self.author, text='Первый!', interest=self.interest)
        Comment.objects.create(user=self.reader, text='В топике', topic=self.topic)

    def urls(self):
        pk = self.interest.pk
        return [
            reverse('users:index'),
            reverse('interests:list'),
            reverse('interests:detail', kwargs={'pk': pk}),
            reverse('interests:users', kwargs={'pk': pk}),
            reverse('interests:comments', kwargs={'pk': pk}),
            reverse('topics:list', kwargs={'pk': pk}),
            reverse('topics:detail', kwargs={'pk': pk, 'slug': self.topic.slug}),
        ]

    def test_pages_render_for_anonymous(self):
        for url in self.urls():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_pages_render_for_logged_in_user(self):
        self.client.force_login(self.reader)
        for url in self.urls() + [reverse('topics:create', kwargs={'pk': self.interest.pk})]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_subscribe_button_reflects_membership(self):
        url = reverse('interests:detail', kwargs={'pk': self.interest.pk})
        self.client.force_login(self.author)
        self.assertContains(self.client.get(url), 'Отписаться')
        self.client.force_login(self.reader)
        self.assertContains(self.client.get(url), 'Подписаться')

    def test_list_page_uses_constant_number_of_queries(self):
        """Счетчики и признак подписки считаются в запросе, а не отдельным запросом на каждую карточку."""
        self.client.force_login(self.reader)
        url = reverse('interests:list')
        with CaptureQueriesContext(connection) as before:
            self.client.get(url)
        for i in range(5):
            make_interest(f'Интерес {i}', self.author)
        with CaptureQueriesContext(connection) as after:
            self.client.get(url)
        self.assertEqual(len(after), len(before))

    def test_pages_are_case_sensitive_template_safe(self):
        """Регрессия: 'interests/...' в extends не находился на Linux."""
        from django.template.loader import get_template
        for name in ('Interests/interest_detail.html', 'Interests/users_list.html', 'Interests/comment_list.html',
                     'topics/topic_detail.html', 'topics/topic_list.html', 'topics/topic_form.html'):
            with self.subTest(template=name):
                get_template(name)
