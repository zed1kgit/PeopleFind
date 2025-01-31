from django.db.models.signals import pre_save
from django.dispatch import receiver

from topics.models import Topic
from topics.utils import slug_generator


@receiver(pre_save, sender=Topic)
def generate_unique_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slug_generator(instance)