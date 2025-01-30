import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PeopleFind.settings')

app = Celery('PeopleFind')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.update({
    'broker_connection_retry_on_startup': True,
})
