import random

from django.core.management import BaseCommand
from django.db.models import Max
from django.db.models.signals import post_save

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
        for i in range(count):
            next_pk = User.objects.all().aggregate(Max('id'))['id__max'] + 1
            if next_pk is None:
                next_pk = 1
            user = User.objects.create(
                email=f'user{next_pk}@gmail.com',
                name=f'User{next_pk}',
                slug=f'user{next_pk}',
                is_active=True,
                is_email_verified=True,
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
