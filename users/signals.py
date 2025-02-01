from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from users.models import User
from users.services import send_mutual_notification_task
from users.tokens import account_activation_token


# @receiver(m2m_changed, sender=User.approved_users.through)
# def mutual_user_mail(sender, instance, action, reverse, model, pk_set, **kwargs):
#     if action == 'post_add':
#         for pk in pk_set:
#             if instance in get_object_or_404(User, pk=pk).approved_users.all():
#                 send_mutual_users_task(instance.pk, pk)


@receiver(m2m_changed, sender=User.approved_users.through)
def send_mutual_approval_notifications(sender, instance, action, reverse, model, pk_set, using, **kwargs):
    if action == 'post_add':
        for user_pk in pk_set:
            other_user = get_object_or_404(User, pk=user_pk)
            if instance in other_user.approved_users.all():
                send_mutual_notification_task(instance, other_user)


@receiver(post_save, sender=User)
def send_confirmation_email(sender, instance, created, **kwargs):
    if created:
        token = account_activation_token.make_token(instance)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        activation_link = f"http://localhost:8000{reverse('users:activate', kwargs={'uidb64': uid, 'token': token})}"
        subject = 'Подтвердите ваш аккаунт'
        message = render_to_string('mails/activation.html', {
            'user': instance,
            'activation_link': activation_link
        })
        from_email = settings.EMAIL_HOST_USER
        to_email = [instance.email]
        msg = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=to_email,
        )
        msg.content_subtype = 'html'
        msg.send()
