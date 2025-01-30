from datetime import datetime, timezone

from django import template

register = template.Library()


@register.filter
def user_media(value):
    if value:
        return fr'/media/{value}'
    return '/static/noavatar.png'

@register.filter
def interest_media(value):
    if value:
        return fr'/media/{value}'
    return '/static/noavatar.png'

@register.filter
def time_since(value):
    now = datetime.now(timezone.utc)
    delta = now - value
    seconds = delta.total_seconds()

    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    if days == 0:
        if hours == 0:
            if minutes == 0:
                return "Только что"
            elif minutes == 1:
                return "1 минуту назад"
            elif minutes <= 4:
                return f"{int(minutes)} минуты назад"
            else:
                return f"{int(minutes)} минут назад"
        elif hours == 1:
            return "1 час назад"
        elif hours <= 4:
            return f"{int(hours)} часа назад"
        else:
            return f"{int(hours)} часов назад"
    elif days == 1:
        return "1 день назад"
    elif days <= 4:
        return f"{int(days)} дня назад"
    else:
        return f"{int(days)} дней назад"