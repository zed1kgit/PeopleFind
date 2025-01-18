from django.db import models
from users.models import User, NULLABLE


class Interest(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')
    logo = models.ImageField(upload_to='interests/', verbose_name='Логотип', **NULLABLE)
    description = models.TextField(verbose_name='Описание', **NULLABLE)
    members = models.ManyToManyField(User, related_name='interests')

    def __str__(self):
        return self.name
