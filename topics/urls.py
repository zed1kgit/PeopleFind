from django.urls import path

from topics.apps import TopicsConfig
from topics.views import CommentCreateView, DeleteObjectView, TopicCreateView, TopicDetailView, TopicListView

app_name = TopicsConfig.name

urlpatterns = [
    path('<int:pk>/create/', TopicCreateView.as_view(), name='create'),
    path('topics/new_comment/', CommentCreateView.as_view(), name='new-comment'),
    path('<int:pk>/topics/<slug:slug>/', TopicDetailView.as_view(), name='detail'),
    path('<int:pk>/topics/', TopicListView.as_view(), name='list'),
    path('delete/', DeleteObjectView.as_view(), name='delete'),
]
