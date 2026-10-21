from functools import partial

from django.conf import settings
from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from users.models import User
from users.tasks import send_activation_email_task, send_mutual_notification_task, send_mutual_users_task


@receiver(m2m_changed, sender=User.approved_users.through)
def notify_mutual_approval(sender, instance, action, reverse, pk_set, **kwargs):
    """Когда пользователь одобряет другого, а тот уже одобрил его, создаем уведомления."""
    if action != 'post_add' or reverse or not pk_set:
        return
    # пользователи из pk_set, которые уже одобрили instance
    mutual_pks = User.objects.filter(pk__in=pk_set, approved_users=instance).values_list('pk', flat=True)
    for other_pk in mutual_pks:
        transaction.on_commit(partial(send_mutual_notification_task.delay, instance.pk, other_pk))
        if settings.MUTUAL_EMAIL_ENABLED:
            transaction.on_commit(partial(send_mutual_users_task.delay, instance.pk, other_pk))


@receiver(post_save, sender=User)
def send_confirmation_email(sender, instance, created, raw=False, **kwargs):
    """Письмо со ссылкой подтверждения: только для новых неподтвержденных пользователей."""
    if created and not raw and not instance.is_email_verified:
        transaction.on_commit(partial(send_activation_email_task.delay, instance.pk))
