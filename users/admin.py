from django.contrib import admin
from users.models import User, Notification


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'slug', 'avatar', 'role', 'pk', 'is_active')
    list_filter = ('name',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date_created')
    list_filter = ('title', 'date_created', 'user')