from django.db import models
from django.contrib.auth.models import AbstractUser

NULLABLE = {'blank': True, 'null': True}


class UserRoles(models.TextChoices):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    role = models.CharField(max_length=9, choices=UserRoles.choices, default=UserRoles.USER)
    name = models.CharField(blank=False, max_length=16, verbose_name='Отображаемое имя')
    nickname = models.SlugField(unique=True, blank=False, db_index=True, max_length=12, verbose_name='Имя пользователя')
    description = models.CharField(max_length=350, verbose_name='Описание', **NULLABLE)
    avatar = models.ImageField(upload_to='users/', verbose_name='Аватар', **NULLABLE)
    is_active = models.BooleanField(default=True, verbose_name='Active')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.email}'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['id']
