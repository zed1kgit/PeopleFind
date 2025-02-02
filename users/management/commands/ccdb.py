from django.core.management.base import BaseCommand
import os
from dotenv import load_dotenv

import psycopg2

class Command(BaseCommand):
    help = 'Создает базу данных в PostgreSQL'

    def handle(self, *args, **kwargs):
        load_dotenv()
        self.stdout.write(f"Создание базы данных {os.getenv('POSTGRES_DATABASE')}...")

        try:
            conn = psycopg2.connect(
                dbname='postgres',
                user=os.getenv('POSTGRES_USER'),
                password=os.getenv('POSTGRES_PASSWORD'),
                host=os.getenv('POSTGRES_HOST'),
                port=os.getenv('POSTGRES_PORT')
            )
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE \"{os.getenv('POSTGRES_DATABASE')}\";")
            self.stdout.write(self.style.SUCCESS(f"База данных {os.getenv('POSTGRES_DATABASE')} успешно создана!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка при создании базы данных: {e}"))
        finally:
            if conn:
                conn.close()