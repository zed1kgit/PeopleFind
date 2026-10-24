# Celery-приложение должно загружаться вместе с Django, чтобы @shared_task
# использовал настройки проекта (брокер и т.д.) и в веб-процессе тоже.
from .celery import app as celery_app

__all__ = ('celery_app',)
