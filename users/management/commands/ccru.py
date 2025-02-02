import random
import os

from django.core.management import BaseCommand
from django.db.models import Max
from django.db.models.signals import post_save
from django.conf import settings

from users.models import User
from users.signals import send_confirmation_email
from Interests.models import Interest


class Command(BaseCommand):
    help = 'Создает случайных пользователей со случайными интересами.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='Количество сгенерированных пользователей'
        )

    def handle(self, *args, **options):
        count = options['count']
        post_save.disconnect(send_confirmation_email, sender=User)
        avatars_dir = os.path.join(settings.MEDIA_ROOT, 'sample')
        avatars = [f for f in os.listdir(avatars_dir) if os.path.isfile(os.path.join(avatars_dir, f))]
        for i in range(count):
            next_pk = User.objects.all().aggregate(Max('id'))['id__max'] + 1
            if next_pk is None:
                next_pk = 1
            random_avatar = random.choice(avatars)
            avatar_path = os.path.join('sample', random_avatar)
            user = User.objects.create(
                email=f'user{next_pk}@gmail.com',
                name=f'User{next_pk}',
                slug=f'user{next_pk}',
                is_active=True,
                is_email_verified=True,
                avatar=avatar_path,
            )

            interests = Interest.objects.all()
            if interests.exists():
                num_interests = random.randint(1, len(interests))
                selected_interests = random.sample(list(interests), k=num_interests)
                for interest in selected_interests:
                    interest.members.add(user)

            user.set_password('qwerty')
            user.save()
            print(f'User{next_pk} created')
        post_save.connect(send_confirmation_email, sender=User)
