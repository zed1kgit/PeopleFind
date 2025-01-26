import random

from django.core.management import BaseCommand
from django.db.models import Max

from users.models import User
from Interests.models import Interest


class Command(BaseCommand):

    def handle(self, *args, **options):
        for i in range(10):
            next_pk = User.objects.all().aggregate(Max('id'))['id__max'] + 1
            if next_pk is None:
                next_pk = 1
            user = User.objects.create(
                email=f'user{next_pk}@gmail.com',
                name=f'User{next_pk}',
                slug=f'user{next_pk}',
                is_active=True,
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
