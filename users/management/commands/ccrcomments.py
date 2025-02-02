import random

from django.core.management.base import BaseCommand

from faker import Faker

from users.models import User
from Interests.models import Interest
from topics.models import Topic, Comment
from topics.utils import slug_generator


class Command(BaseCommand):
    help = 'Создает случайные комментарии от случайных пользователей со случайными интересами или топиками.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Количество комментариев для создания (по умолчанию 10).',
        )
        parser.add_argument(
            '--user_id',
            type=int,
            default=None,
            help='ID пользователя, который будет автором комментариев. Если не указан, будет выбран случайный пользователь.',
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--interest_id',
            type=int,
            default=None,
            help='ID интереса, к которому будут привязаны комментарии. Если не указан, будет выбран случайный интерес.',
        )
        group.add_argument(
            '--topic_id',
            type=int,
            default=None,
            help='ID топика, к которому будут привязаны комментарии. Если не указан, будет выбран случайный интерес.',
        )

    def handle(self, *args, **options):
        fake = Faker()
        count = options['count']
        user_id = options['user_id']
        interest_id = options['interest_id']
        topic_id = options['topic_id']
        interest = None
        topic = None

        for _ in range(count):
            if user_id:
                user = User.objects.get(id=user_id)
            else:
                user = User.objects.order_by('?').first()

            if not interest_id and not topic_id:
                variants = [
                    {'interest': Interest.objects.order_by('?').first()},
                    {'topic': Topic.objects.order_by('?').first()}
                ]
                chosen_variant = random.choice(variants)
                if 'interest' in chosen_variant:
                    interest = chosen_variant['interest']
                    if not interest:
                        self.stdout.write(self.style.ERROR('Нету интересов в базе данных. Сначала создайте интересы.'))
                        return
                elif 'topic' in chosen_variant:
                    topic = chosen_variant['topic']
                    if not topic:
                        self.stdout.write(self.style.ERROR('Нету топиков в базе данных. Сначала создайте топики.'))
                        return
            elif interest_id:
                    interest = Interest.objects.get(id=interest_id)
                    if not interest:
                        self.stdout.write(self.style.ERROR('Нет интереса в базе данных. Сначала создайте интерес.'))
                        return
            elif topic_id:
                    topic = Topic.objects.get(id=interest_id)
                    if not topic:
                        self.stdout.write(
                            self.style.ERROR('Нет топика в базе данных. Сначала создайте топик.'))
                        return

            if not user:
                self.stdout.write(self.style.ERROR('Нет пользователей в базе данных. Сначала создайте пользователей.'))
                return

            text = fake.text(max_nb_chars=200)

            comment = Comment.objects.create(
                user=user,
                text=text,
                interest=interest,
                topic=topic,
            )
            comment.save()

        self.stdout.write(self.style.SUCCESS(f'Успешно создано {count} комментариев.'))
