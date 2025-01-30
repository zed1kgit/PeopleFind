from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.shortcuts import get_object_or_404

from users.models import User
from users.services import send_mutual_notification_task


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