from django.urls import path

from Interests.apps import InterestsConfig
from Interests.views import InterestCreate, InterestUpdate, InterestDelete, InterestDetailView, InterestListView

app_name = InterestsConfig.name

urlpatterns = [
    path('create/', InterestCreate.as_view(), name='create'),
    path('<int:pk>/update/', InterestUpdate.as_view(), name='update'),
    path('<int:pk>/delete/', InterestDelete.as_view(), name='delete'),
    path('<int:pk>/', InterestDetailView.as_view(), name='detail'),
    path('list/', InterestListView.as_view(), name='list'),
]
