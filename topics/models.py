from django.db import models

from Interests.models import Interest
from users.models import User, NULLABLE


class Topic(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Текст топика", **NULLABLE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, **NULLABLE, related_name="topics")
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE, related_name='topics', verbose_name="Интерес",
                                 **NULLABLE)
    slug = models.SlugField(unique=True, db_index=True, verbose_name='URL', max_length=255)

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата написания")
    text = models.TextField(verbose_name="Комментарий", blank=True, null=True)
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE, **NULLABLE, related_name='comments')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, **NULLABLE, related_name='comments')

    def __str__(self):
        return f"{self.user}: {self.text}"