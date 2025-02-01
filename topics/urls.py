from django.urls import path
from django.views.decorators.cache import never_cache

from topics.apps import TopicsConfig
from topics.views import TopicCreateView, CommentCreateView, TopicDetailView, TopicListView, DeleteView

app_name = TopicsConfig.name

urlpatterns = [
    path('<int:pk>/create/', TopicCreateView.as_view(), name='create'),
    path('topics/new_comment/', CommentCreateView.as_view(), name='new-comment'),
    path('<int:pk>/topics/<slug:slug>/', TopicDetailView.as_view(), name='detail'),
    path('<int:pk>/topics/', TopicListView.as_view(), name='list'),
    path('delete/', DeleteView.as_view(), name='delete'),
]