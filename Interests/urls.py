from django.urls import path

from Interests.apps import InterestsConfig
from Interests.views import InterestCreate, InterestUpdate, InterestDelete, InterestDetailView, InterestListView, \
    FoundSimilarUserView, DenySimilarUserView, FindSimilarUser, ApproveSimilarUserView, ToggleInterestView

app_name = InterestsConfig.name

urlpatterns = [
    path('create/', InterestCreate.as_view(), name='create'),
    path('<int:pk>/update/', InterestUpdate.as_view(), name='update'),
    path('<int:pk>/delete/', InterestDelete.as_view(), name='delete'),
    path('<int:pk>/', InterestDetailView.as_view(), name='detail'),
    path('', InterestListView.as_view(), name='list'),
    path('find-user/', FindSimilarUser.as_view(), name='find-user'),
    path('user-found/', FoundSimilarUserView.as_view(), name='user-found'),
    path('deny-user/', DenySimilarUserView.as_view(), name='deny-user'),
    path('approve-user/', ApproveSimilarUserView.as_view(), name='approve-user'),
    path('toggle-interest/<int:pk>/', ToggleInterestView.as_view(), name='toggle-interest'),
]
