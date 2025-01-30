from django.conf import settings
from django.core.mail import EmailMessage
from celery import shared_task
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy

from users.models import User, Notification


def send_approval_notification(user1, user2):
    notification1 = Notification.objects.create(
        title=f"Взаимное одобрение",
        message=f"Пользователь <a href='{reverse_lazy("users:profile", kwargs={'slug': user2.slug})}' title='{user2.name}'>{user2.name}</a> также одобрил вас!",
        user=user1
    )
    user1.notifications.add(notification1)

    notification2 = Notification.objects.create(
        title=f"Взаимное одобрение",
        message=f"Пользователь <a href='{reverse_lazy("users:profile", kwargs={'slug': user1.slug})}' title='{user1.name}'>{user1.name}</a> также одобрил вас!",
        user=user2
    )
    user2.notifications.add(notification2)


def send_mutual_users_mail(obj, obj2):
    context = {
        'name': obj.name,
        'url': reverse_lazy('users:profile', kwargs={'slug': obj.slug}),
    }
    message = render_to_string('mails/mutual.html', context)
    msg = EmailMessage(
        subject=f'Есть взаимность!!',
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=[obj2.email],
    )
    msg.content_subtype = 'html'
    msg.send()
    context2 = {
        'name': obj2.name,
        'url': reverse_lazy('users:profile', kwargs={'slug': obj2.slug}),
    }
    message2 = render_to_string('mails/mutual.html', context2)
    msg2 = EmailMessage(
        subject=f'Есть взаимность!!',
        body=message2,
        from_email=settings.EMAIL_HOST_USER,
        to=[obj.email],
    )
    msg2.content_subtype = 'html'
    msg2.send()


@shared_task
def send_mutual_users_task(pk, pk2):
    obj = get_object_or_404(User, id=pk)
    obj2 = get_object_or_404(User, id=pk2)
    return send_mutual_users_mail(obj, obj2)


@shared_task
def send_mutual_notification_task(user1, user2):
    return send_approval_notification(user1, user2)