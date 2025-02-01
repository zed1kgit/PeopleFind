import random

from django.db.models import Count

from users.models import User


def find_similar_users(current_user):
    current_user_interests = current_user.interests.all()
    current_user_exclude_pks = list(current_user.approved_users.values_list('pk', flat=True)) + list(
        current_user.denied_users.values_list('pk', flat=True)) + [current_user.pk]
    similar_users = User.objects.filter(interests__in=current_user_interests).exclude(id__in=current_user_exclude_pks)
    similar_users = similar_users.annotate(common_interests_count=Count('interests'))
    similar_users_list = list(similar_users.values_list('pk', 'common_interests_count'))
    return similar_users_list


def weighted_random_choice(similar_users_list):
    total_weight = sum(weight for _, weight in similar_users_list)
    rnd = random.uniform(0, total_weight)
    upto = 0
    for user_pk, weight in similar_users_list:
        if upto + weight >= rnd:
            return user_pk
        upto += weight
    assert False, "Shouldn't get here"


def find_people (current_user):
    similar_users_list = find_similar_users(current_user)
    if len(similar_users_list) > 0:
        found_user_pk = weighted_random_choice(similar_users_list)
        found_user = User.objects.get(pk=found_user_pk)
        return found_user
    else:
        return None
