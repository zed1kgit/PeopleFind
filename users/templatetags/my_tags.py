from django import template
from django.templatetags.static import static

register = template.Library()


def media_url(value):
    """URL загруженного файла (с учетом MEDIA_URL) или заглушка, если файла нет."""
    if value:
        return value.url
    return static('noavatar.png')


register.filter('user_media', media_url)
register.filter('interest_media', media_url)


@register.simple_tag
def elided_page_range(page_obj):
    """Номера страниц с многоточием: 1 … 4 5 [6] 7 8 … 20."""
    return page_obj.paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)
