from django.db import models
from django.db.models import BooleanField, Count, Exists, OuterRef, Value

from users.models import NULLABLE, User


class InterestQuerySet(models.QuerySet):
    def with_stats(self, user=None):
        """Добавляет members_count и is_member (подписан ли user) одним запросом."""
        queryset = self.annotate(members_count=Count('members', distinct=True))
        if user is not None and user.is_authenticated:
            through = self.model.members.through
            is_member = Exists(through.objects.filter(interest_id=OuterRef('pk'), user_id=user.pk))
        else:
            is_member = Value(False, output_field=BooleanField())
        return queryset.annotate(is_member=is_member)


class Interest(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Название')
    logo = models.ImageField(upload_to='interests/', verbose_name='Логотип', **NULLABLE)
    description = models.TextField(verbose_name='Описание', **NULLABLE)
    members = models.ManyToManyField(User, related_name='interests', blank=True)

    objects = InterestQuerySet.as_manager()

    def __str__(self):
        return self.name
