from django.contrib import admin
from topics.models import Topic, Comment


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'interest', 'author', 'created_at', 'pk',)
    list_filter = ('interest',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'created_at', 'pk',)
    list_filter = ('user', 'created_at',)