import random

from django.core.management.base import BaseCommand, CommandError
from faker import Faker

from Interests.models import Interest
from topics.models import Comment, Topic
from users.models import User


class Command(BaseCommand):
    help = 'Создает случайные комментарии от случайных пользователей к интересам или топикам.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10,
                            help='Количество комментариев для создания (по умолчанию 10).')
        parser.add_argument('--user_id', type=int, default=None,
                            help='ID автора комментариев. Если не указан, будет выбран случайный пользователь.')
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--interest_id', type=int, default=None,
                           help='ID интереса. Если не указан ни интерес, ни топик, цель выбирается случайно.')
        group.add_argument('--topic_id', type=int, default=None,
                           help='ID топика. Если не указан ни интерес, ни топик, цель выбирается случайно.')

    def handle(self, *args, **options):
        fake = Faker('ru_RU')

        for _ in range(options['count']):
            if options['user_id']:
                user = User.objects.filter(id=options['user_id']).first()
            else:
                user = User.objects.order_by('?').first()
            if not user:
                raise CommandError('Пользователь не найден. Сначала создайте пользователей.')

            interest = topic = None
            if options['interest_id']:
                interest = Interest.objects.filter(id=options['interest_id']).first()
                if not interest:
                    raise CommandError('Интерес не найден.')
            elif options['topic_id']:
                topic = Topic.objects.filter(id=options['topic_id']).first()
                if not topic:
                    raise CommandError('Топик не найден.')
            else:
                candidates = [c for c in (Interest.objects.order_by('?').first(),
                                          Topic.objects.order_by('?').first()) if c]
                if not candidates:
                    raise CommandError('Нет ни интересов, ни топиков. Сначала создайте их.')
                target = random.choice(candidates)
                if isinstance(target, Interest):
                    interest = target
                else:
                    topic = target

            Comment.objects.create(user=user, text=fake.text(max_nb_chars=200), interest=interest, topic=topic)

        self.stdout.write(self.style.SUCCESS(f"Успешно создано {options['count']} комментариев."))
