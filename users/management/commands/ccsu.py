from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        admin = User.objects.create(
            email='admin@gmail.com',
            name='Admin',
            slug='admin',
            role='admin',
            is_staff=True,
            is_superuser=True,
            is_active=True,
            is_email_verified=True,
        )

        admin.set_password('qwerty')
        admin.save()
        print('Admin created')
