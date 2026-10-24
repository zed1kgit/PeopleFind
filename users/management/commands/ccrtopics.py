from django.core.management.base import BaseCommand, CommandError
from faker import Faker

from Interests.models import Interest
from topics.models import Topic
from users.models import User


class Command(BaseCommand):
    help = 'Создает случайные топики со случайными пользователями и интересами.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10,
                            help='Количество топиков для создания (по умолчанию 10).')
        parser.add_argument('--user_id', type=int, default=None,
                            help='ID автора топиков. Если не указан, будет выбран случайный пользователь.')
        parser.add_argument('--interest_id', type=int, default=None,
                            help='ID интереса. Если не указан, будет выбран случайный интерес.')

    def handle(self, *args, **options):
        fake = Faker('ru_RU')

        for _ in range(options['count']):
            if options['user_id']:
                author = User.objects.filter(id=options['user_id']).first()
            else:
                author = User.objects.order_by('?').first()
            if not author:
                raise CommandError('Пользователь не найден. Сначала создайте пользователей.')

            if options['interest_id']:
                interest = Interest.objects.filter(id=options['interest_id']).first()
            else:
                interest = Interest.objects.order_by('?').first()
            if not interest:
                raise CommandError('Интерес не найден. Сначала загрузите интересы (loaddata interests.json).')

            # slug генерируется автоматически сигналом pre_save
            Topic.objects.create(
                title=fake.sentence(nb_words=6),
                description=fake.text(max_nb_chars=500),
                author=author,
                interest=interest,
            )

        self.stdout.write(self.style.SUCCESS(f"Успешно создано {options['count']} топиков."))
