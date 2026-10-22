from unittest import mock

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from PeopleFind.testing import PASSWORD, make_user
from users.models import Notification, User, UserRoles
from users.tasks import MUTUAL_TITLE, send_activation_email_task, send_mutual_notification_task
from users.tokens import account_activation_token


class UserManagerTests(TestCase):
    def test_create_user_fills_slug_and_name_from_email(self):
        user = User.objects.create_user(email='john.smith@example.com', password=PASSWORD)
        self.assertEqual(user.slug, 'johnsmith')   # точка недопустима в <slug:slug>
        self.assertEqual(user.name, 'johnsmith')
        self.assertTrue(user.check_password(PASSWORD))
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(email='root@example.com', password=PASSWORD)
        self.assertTrue(admin.is_staff and admin.is_superuser)
        self.assertEqual(admin.role, UserRoles.ADMIN)
        self.assertTrue(admin.is_email_verified)

    def test_slug_is_unique(self):
        first = User.objects.create_user(email='a.b@example.com', password=PASSWORD)
        second = User.objects.create_user(email='ab@example.com', password=PASSWORD)
        self.assertNotEqual(first.slug, second.slug)

    def test_email_is_required(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password=PASSWORD)


class ActivationEmailTests(TestCase):
    def test_signal_queues_email_for_new_unverified_user(self):
        with mock.patch.object(send_activation_email_task, 'delay') as delay:
            with self.captureOnCommitCallbacks(execute=True):
                user = make_user(1, is_email_verified=False)
        delay.assert_called_once_with(user.pk)

    def test_signal_skips_verified_user(self):
        with mock.patch.object(send_activation_email_task, 'delay') as delay:
            with self.captureOnCommitCallbacks(execute=True):
                make_user(1, is_email_verified=True)
        delay.assert_not_called()

    def test_task_sends_email_with_absolute_link(self):
        user = make_user(1, is_email_verified=False)
        send_activation_email_task(user.pk)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [user.email])
        self.assertIn('http://', mail.outbox[0].body)
        self.assertIn('/activate/', mail.outbox[0].body)

    def test_task_does_nothing_for_verified_user(self):
        user = make_user(1)
        send_activation_email_task(user.pk)
        self.assertEqual(len(mail.outbox), 0)


class ActivateAccountViewTests(TestCase):
    def setUp(self):
        self.user = make_user(1, is_email_verified=False)

    def activation_url(self, token):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        return reverse('users:activate', kwargs={'uidb64': uid, 'token': token})

    def test_valid_link_verifies_user(self):
        response = self.client.get(self.activation_url(account_activation_token.make_token(self.user)))
        self.assertRedirects(response, reverse('users:login'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_invalid_token_does_not_verify(self):
        response = self.client.get(self.activation_url('bad-token'))
        self.assertRedirects(response, reverse('users:register'))
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_email_verified)

    def test_garbage_uid_gives_redirect_not_error(self):
        response = self.client.get(reverse('users:activate', kwargs={'uidb64': 'xx', 'token': 'yy'}))
        self.assertEqual(response.status_code, 302)


class LoginAndMiddlewareTests(TestCase):
    def test_unverified_user_cannot_log_in(self):
        user = make_user(1, is_email_verified=False)
        response = self.client.post(reverse('users:login'), {'username': user.email, 'password': PASSWORD})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Подтвердите почту')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_verified_user_can_log_in(self):
        user = make_user(1)
        response = self.client.post(reverse('users:login'), {'username': user.email, 'password': PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_middleware_redirects_unverified_session_before_view(self):
        user = make_user(1, is_email_verified=False)
        self.client.force_login(user)
        response = self.client.get(reverse('interests:list'))
        self.assertRedirects(response, reverse('users:login'))

    def test_middleware_allows_login_page_for_unverified_session(self):
        user = make_user(1, is_email_verified=False)
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse('users:login')).status_code, 200)

    def test_verified_user_is_not_redirected(self):
        self.client.force_login(make_user(1))
        self.assertEqual(self.client.get(reverse('interests:list')).status_code, 200)


class ProfileViewsTests(TestCase):
    def setUp(self):
        self.user = make_user(1)

    def test_profile_page(self):
        response = self.client.get(reverse('users:profile', kwargs={'slug': self.user.slug}))
        self.assertContains(response, self.user.name)

    def test_profile_id_redirect_and_404(self):
        response = self.client.get(reverse('users:profile-id-redirect', kwargs={'pk': self.user.pk}))
        self.assertRedirects(response, reverse('users:profile', kwargs={'slug': self.user.slug}))
        self.assertEqual(self.client.get(reverse('users:profile-id-redirect', kwargs={'pk': 9999})).status_code, 404)

    def test_password_change_redirects_to_profile(self):
        self.client.force_login(self.user)
        new_password = 'Another-Str0ng-pass-987'
        response = self.client.post(reverse('users:change-password', kwargs={'slug': self.user.slug}), {
            'old_password': PASSWORD,
            'new_password1': new_password,
            'new_password2': new_password,
        })
        self.assertRedirects(response, reverse('users:profile', kwargs={'slug': self.user.slug}),
                             fetch_redirect_response=False)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

    def test_index_page(self):
        self.assertEqual(self.client.get(reverse('users:index')).status_code, 200)


class NotificationTests(TestCase):
    def setUp(self):
        self.alice = make_user(1)
        self.bob = make_user(2, name='<u>zz</u>', contacts='<i>tg</i>')

    def test_notification_does_not_render_user_html(self):
        """Регрессия: имя и контакты раньше попадали в страницу как HTML (|safe)."""
        Notification.objects.create(user=self.alice, from_user=self.bob, title=MUTUAL_TITLE, message='m')
        self.client.force_login(self.alice)
        response = self.client.get(reverse('users:notifications'))
        self.assertNotContains(response, '<u>zz</u>')
        self.assertNotContains(response, '<i>tg</i>')
        self.assertContains(response, '&lt;u&gt;zz&lt;/u&gt;')

    def test_mark_as_read_only_for_owner(self):
        notification = Notification.objects.create(user=self.alice, title='t', message='m')
        self.client.force_login(self.bob)
        url = reverse('users:mark_as_read', kwargs={'pk': notification.pk})
        self.assertEqual(self.client.post(url).status_code, 404)
        self.client.force_login(self.alice)
        self.assertEqual(self.client.post(url).json(), {'success': True})
        notification.refresh_from_db()
        self.assertTrue(notification.viewed)

    def test_unread_count_in_header(self):
        Notification.objects.create(user=self.alice, title='t', message='m')
        Notification.objects.create(user=self.alice, title='t2', message='m', viewed=True)
        self.client.force_login(self.alice)
        response = self.client.get(reverse('users:index'))
        self.assertEqual(response.context['unread_notifications_count'], 1)

    def test_notifications_are_paginated(self):
        for i in range(25):
            Notification.objects.create(user=self.alice, title=f'n{i}', message='m')
        self.client.force_login(self.alice)
        response = self.client.get(reverse('users:notifications'))
        self.assertEqual(len(response.context['object_list']), 20)


class MutualApprovalTests(TestCase):
    def setUp(self):
        self.alice = make_user(1)
        self.bob = make_user(2)

    def test_one_sided_approval_creates_nothing(self):
        with mock.patch.object(send_mutual_notification_task, 'delay') as delay:
            with self.captureOnCommitCallbacks(execute=True):
                self.alice.approved_users.add(self.bob)
        delay.assert_not_called()

    def test_mutual_approval_queues_notification(self):
        self.alice.approved_users.add(self.bob)
        with mock.patch.object(send_mutual_notification_task, 'delay') as delay:
            with self.captureOnCommitCallbacks(execute=True):
                self.bob.approved_users.add(self.alice)
        delay.assert_called_once_with(self.bob.pk, self.alice.pk)

    def test_task_creates_one_notification_per_user_and_is_idempotent(self):
        send_mutual_notification_task(self.alice.pk, self.bob.pk)
        send_mutual_notification_task(self.alice.pk, self.bob.pk)
        self.assertEqual(Notification.objects.filter(user=self.alice, from_user=self.bob).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.bob, from_user=self.alice).count(), 1)

    def test_mutual_users_list_shows_only_mutual(self):
        carol = make_user(3)
        self.alice.approved_users.add(self.bob, carol)
        self.bob.approved_users.add(self.alice)
        self.client.force_login(self.alice)
        response = self.client.get(reverse('users:mutual-list'))
        self.assertEqual(list(response.context['object_list']), [self.bob])
