import uuid
from django.utils.text import slugify

from topics.models import Topic


def slug_generator(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)
    if Topic.objects.filter(slug=slug).exists():
        new_slug = f"{slug}-{uuid.uuid4().hex[:6]}"
        return slug_generator(instance, new_slug=new_slug)
    return slug