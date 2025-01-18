from django.contrib import admin
from Interests.models import Interest


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo', 'description', 'pk',)
    list_filter = ('name',)