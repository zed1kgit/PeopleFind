import os

from django.conf import settings
from django.core.management import BaseCommand, CommandError

from users.models import User, UserRoles


class Command(BaseCommand):
    help = 'Создает администратора. Пароль: --password, переменная ADMIN_PASSWORD (или qwerty при DEBUG=1).'

    def add_arguments(self, parser):
        parser.add_argument('--email', default='admin@example.com', help='Email администратора')
        parser.add_argument('--password', default=None, help='Пароль администратора')

    def handle(self, *args, **options):
        password = options['password'] or os.getenv('ADMIN_PASSWORD') or ('qwerty' if settings.DEBUG else None)
        if not password:
            raise CommandError('Укажите пароль: --password или переменную окружения ADMIN_PASSWORD.')

        if User.objects.filter(email=options['email']).exists():
            self.stdout.write(self.style.WARNING(f"Пользователь {options['email']} уже существует."))
            return

        User.objects.create_superuser(
            email=options['email'],
            password=password,
            name='Admin',
            slug='admin',
            role=UserRoles.ADMIN,
        )
        self.stdout.write(self.style.SUCCESS(f"Администратор {options['email']} создан."))
