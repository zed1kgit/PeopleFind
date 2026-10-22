from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse_lazy
from django.utils.text import slugify

NULLABLE = {'blank': True, 'null': True}


class UserRoles(models.TextChoices):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'


class UserManager(BaseUserManager):
    """Менеджер для модели без username: вход по email.

    Стандартный UserManager из Django передаёт в модель username, которого здесь
    нет, поэтому createsuperuser с ним не работает.
    """
    use_in_migrations = True

    def _unique_slug(self, email):
        """slug из локальной части email: только допустимые для URL символы, уникальный."""
        base = slugify(email.split('@')[0])[:8] or 'user'
        slug, number = base, 1
        while self.model.objects.filter(slug=slug).exists():
            number += 1
            slug = f'{base}{number}'
        return slug[:12]

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        extra_fields.setdefault('slug', self._unique_slug(email))
        extra_fields.setdefault('name', extra_fields['slug'][:16])
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRoles.ADMIN)
        extra_fields.setdefault('is_email_verified', True)
        if extra_fields['is_staff'] is not True or extra_fields['is_superuser'] is not True:
            raise ValueError('У суперпользователя должны быть is_staff=True и is_superuser=True')
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None
    email = models.EmailField(unique=True, verbose_name='Email')
    role = models.CharField(max_length=9, choices=UserRoles.choices, default=UserRoles.USER)
    name = models.CharField(blank=False, max_length=16, verbose_name='Отображаемое имя')
    slug = models.SlugField(unique=True, blank=False, db_index=True, max_length=12, verbose_name='Имя пользователя')
    description = models.TextField(max_length=350, verbose_name='Описание', **NULLABLE)
    contacts = models.CharField(max_length=255, verbose_name='Контакты для связи', default='Отсутствуют', **NULLABLE)
    avatar = models.ImageField(upload_to='users/', verbose_name='Аватар', **NULLABLE)
    is_active = models.BooleanField(default=True, verbose_name='Active')
    approved_users = models.ManyToManyField('self', symmetrical=False, related_name="approved", blank=True)
    denied_users = models.ManyToManyField('self', symmetrical=False, related_name="denied", blank=True)
    is_email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse_lazy('users:profile', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['id']


class Notification(models.Model):
    """Уведомление пользователя.

    message - обычный текст (в шаблоне экранируется). Если уведомление связано
    с другим пользователем (например, взаимное одобрение), он хранится в from_user,
    а ссылка на профиль строится в шаблоне, а не вшивается в текст как HTML.
    """
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='+', **NULLABLE)
    date_created = models.DateTimeField(auto_now_add=True)
    viewed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_created']
        indexes = [models.Index(fields=['user', 'viewed'])]

    def __str__(self):
        return f"{self.title}: {self.message}"