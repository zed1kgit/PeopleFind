import os
import random

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.db.models import Max

from Interests.models import Interest
from users.models import User

DEV_PASSWORD = 'qwerty'


class Command(BaseCommand):
    help = 'Создает случайных пользователей со случайными интересами (только при DEBUG=1, пароль: qwerty).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Количество сгенерированных пользователей (по умолчанию 5)',
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Команда создает пользователей с известным паролем и доступна только при DEBUG=1.')

        avatars_dir = os.path.join(settings.MEDIA_ROOT, 'sample')
        avatars = []
        if os.path.isdir(avatars_dir):
            avatars = [f for f in os.listdir(avatars_dir) if os.path.isfile(os.path.join(avatars_dir, f))]

        interests = list(Interest.objects.all())
        last_id = User.objects.aggregate(Max('id'))['id__max'] or 0

        for i in range(options['count']):
            number = last_id + i + 1
            user = User(
                email=f'user{number}@example.com',
                name=f'User{number}',
                slug=f'user{number}',
                is_active=True,
                is_email_verified=True,
                avatar=os.path.join('sample', random.choice(avatars)) if avatars else None,
            )
            user.set_password(DEV_PASSWORD)
            user.save()

            if interests:
                user.interests.add(*random.sample(interests, k=random.randint(1, len(interests))))
            self.stdout.write(f'User{number} created')
