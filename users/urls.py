from django.urls import path

from users.apps import UsersConfig
from users.views import index

app_name = UsersConfig.name

urlpatterns = [
    path('', index, name='index'),
]