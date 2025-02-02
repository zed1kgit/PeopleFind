from django.core.management.base import BaseCommand

from faker import Faker

from users.models import User
from Interests.models import Interest
from topics.models import Topic
from topics.utils import slug_generator


class Command(BaseCommand):
    help = 'Создает случайные топики со случайными пользователями и интересами.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Количество топиков для создания (по умолчанию 10).',
        )
        parser.add_argument(
            '--user_id',
            type=int,
            default=None,
            help='ID пользователя, который будет автором топиков. Если не указан, будет выбран случайный пользователь.',
        )
        parser.add_argument(
            '--interest_id',
            type=int,
            default=None,
            help='ID интереса, к которому будут привязаны топики. Если не указан, будет выбран случайный интерес.',
        )

    def handle(self, *args, **options):
        fake = Faker()
        count = options['count']
        user_id = options['user_id']
        interest_id = options['interest_id']

        for _ in range(count):
            if user_id:
                author = User.objects.get(id=user_id)
            else:
                author = User.objects.order_by('?').first()

            if interest_id:
                interest = Interest.objects.get(id=interest_id)
            else:
                interest = Interest.objects.order_by('?').first()

            if not author:
                self.stdout.write(self.style.ERROR('Нет пользователей в базе данных. Сначала создайте пользователей.'))
                return

            if not interest:
                self.stdout.write(self.style.ERROR('Нет интересов в базе данных. Сначала создайте интересы.'))
                return

            title = fake.sentence(nb_words=6)
            description = fake.text(max_nb_chars=500)

            topic = Topic.objects.create(
                title=title,
                description=description,
                author=author,
                interest=interest,
            )
            topic.slug = slug_generator(topic)
            topic.save()

        self.stdout.write(self.style.SUCCESS(f'Успешно создано {count} топиков.'))
