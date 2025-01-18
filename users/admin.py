from django.contrib import admin
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'slug', 'avatar', 'role', 'pk', 'is_active')
    list_filter = ('name',)
