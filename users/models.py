from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse_lazy

NULLABLE = {'blank': True, 'null': True}


class UserRoles(models.TextChoices):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None
    email = models.EmailField(unique=True, verbose_name='Email')
    role = models.CharField(max_length=9, choices=UserRoles.choices, default=UserRoles.USER)
    name = models.CharField(blank=False, max_length=16, verbose_name='Отображаемое имя')
    slug = models.SlugField(unique=True, blank=False, db_index=True, max_length=12, verbose_name='Имя пользователя')
    description = models.TextField(max_length=350, verbose_name='Описание', **NULLABLE)
    avatar = models.ImageField(upload_to='users/', verbose_name='Аватар', **NULLABLE)
    is_active = models.BooleanField(default=True, verbose_name='Active')
    approved_users = models.ManyToManyField('self', symmetrical=False, related_name="approved", blank=True)
    denied_users = models.ManyToManyField('self', symmetrical=False, related_name="denied", blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.name}'

    def get_unread_notifications_count(self):
        return self.notifications.filter(viewed=False).count()

    def get_absolute_url(self):
        return reverse_lazy('users:profile', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['id']


class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    viewed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}: {self.message}"