"""Фабрики для тестов."""
from Interests.models import Interest
from users.models import User

PASSWORD = 'pass12345-Test'


def make_user(number, **kwargs):
    """Подтвержденный пользователь userN@example.com с паролем PASSWORD."""
    params = {
        'email': f'user{number}@example.com',
        'name': f'User{number}',
        'slug': f'user{number}',
        'is_email_verified': True,
    }
    params.update(kwargs)
    return User.objects.create_user(password=PASSWORD, **params)


def make_interest(name, *members):
    interest = Interest.objects.create(name=name)
    interest.members.add(*members)
    return interest
