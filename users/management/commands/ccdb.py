import psycopg2
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from psycopg2 import errors, sql


class Command(BaseCommand):
    help = 'Создает базу данных PostgreSQL с параметрами из .env'

    def handle(self, *args, **options):
        db = settings.DATABASES['default']
        if 'postgresql' not in db['ENGINE']:
            raise CommandError('PostgreSQL не настроен (POSTGRES_DATABASE пуст). SQLite создается автоматически.')

        self.stdout.write(f"Создание базы данных {db['NAME']}...")
        conn = None
        try:
            conn = psycopg2.connect(
                dbname='postgres',
                user=db['USER'],
                password=db['PASSWORD'],
                host=db['HOST'],
                port=db['PORT'],
            )
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(db['NAME'])))
            self.stdout.write(self.style.SUCCESS(f"База данных {db['NAME']} успешно создана!"))
        except errors.DuplicateDatabase:
            self.stdout.write(self.style.WARNING(f"База данных {db['NAME']} уже существует."))
        except psycopg2.Error as e:
            raise CommandError(f'Ошибка при создании базы данных: {e}')
        finally:
            if conn:
                conn.close()
