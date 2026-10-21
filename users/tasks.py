from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from users.models import Notification, User
from users.tokens import account_activation_token

MUTUAL_TITLE = 'Взаимное одобрение'


def absolute_url(path):
    return f'{settings.SITE_URL}{path}'


def _send_html_mail(subject, template, context, to_email):
    message = EmailMessage(
        subject=subject,
        body=render_to_string(template, context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    message.content_subtype = 'html'
    message.send()


# В задачи передаются только id: объекты моделей не сериализуются в JSON, а к моменту
# выполнения задачи данные могли измениться.

@shared_task
def send_activation_email_task(user_pk):
    user = User.objects.filter(pk=user_pk).first()
    if user is None or user.is_email_verified:
        return
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    link = absolute_url(reverse('users:activate', kwargs={'uidb64': uid, 'token': token}))
    _send_html_mail('Подтвердите ваш аккаунт', 'mails/activation.html',
                    {'user': user, 'activation_link': link}, user.email)


@shared_task
def send_mutual_notification_task(user1_pk, user2_pk):
    users = {u.pk: u for u in User.objects.filter(pk__in=[user1_pk, user2_pk])}
    if len(users) != 2:
        return
    user1, user2 = users[user1_pk], users[user2_pk]
    for recipient, other in ((user1, user2), (user2, user1)):
        Notification.objects.get_or_create(
            user=recipient,
            from_user=other,
            title=MUTUAL_TITLE,
            defaults={'message': f'Пользователь {other.name} также одобрил вас!'},
        )


@shared_task
def send_mutual_users_task(user1_pk, user2_pk):
    users = {u.pk: u for u in User.objects.filter(pk__in=[user1_pk, user2_pk])}
    if len(users) != 2:
        return
    for recipient, other in ((users[user1_pk], users[user2_pk]), (users[user2_pk], users[user1_pk])):
        url = absolute_url(reverse('users:profile', kwargs={'slug': other.slug}))
        _send_html_mail('Есть взаимность!', 'mails/mutual.html', {'name': other.name, 'url': url}, recipient.email)
