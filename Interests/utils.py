import random

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from Interests.models import Interest
from users.models import User

CANDIDATES_LIMIT = 50


def find_similar_users(current_user, limit=CANDIDATES_LIMIT):
    """Кандидаты с общими интересами, которых текущий пользователь еще не оценил.

    Раньше в Python загружались все подходящие пользователи при каждом клике.
    Теперь БД отбирает не больше limit лучших (по числу общих интересов), а у
    каждого объекта есть атрибут common_interests_count.
    """
    interest_ids = list(current_user.interests.values_list('pk', flat=True))
    if not interest_ids:
        return []
    return list(
        User.objects.filter(is_active=True, is_email_verified=True)
        .exclude(pk=current_user.pk)
        .exclude(pk__in=current_user.approved_users.values('pk'))
        .exclude(pk__in=current_user.denied_users.values('pk'))
        .annotate(common_interests_count=Count('interests', filter=Q(interests__in=interest_ids)))
        .filter(common_interests_count__gt=0)
        .order_by('-common_interests_count', '?')[:limit]
    )


def weighted_random_choice(candidates):
    """Случайный кандидат; чем больше общих интересов, тем выше шанс."""
    weights = [candidate.common_interests_count for candidate in candidates]
    return random.choices(candidates, weights=weights, k=1)[0]


def find_people(current_user):
    candidates = find_similar_users(current_user)
    return weighted_random_choice(candidates) if candidates else None


def get_interest_or_404(request, pk):
    """Интерес со счетчиком участников и признаком подписки текущего пользователя."""
    return get_object_or_404(Interest.objects.with_stats(request.user), pk=pk)


def interest_sidebar_context(interest):
    """Данные для interest_base.html: боковая панель и счетчики."""
    return {
        'members_preview': interest.members.all()[:12],
        'topics_count': interest.topics.count(),
        'comments_count': interest.comments.count(),
    }
