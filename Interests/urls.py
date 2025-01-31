from django.urls import path
from django.views.decorators.cache import never_cache

from Interests.apps import InterestsConfig
from Interests.views import InterestCreate, InterestUpdate, InterestDelete, InterestDetailView, InterestListView, \
    FoundSimilarUserView, DenySimilarUserView, FindSimilarUser, ApproveSimilarUserView, ToggleInterestView, \
    InterestCommentsListView

app_name = InterestsConfig.name

urlpatterns = [
    path('create/', never_cache(InterestCreate.as_view()), name='create'),
    path('<int:pk>/update/', never_cache(InterestUpdate.as_view()), name='update'),
    path('<int:pk>/delete/', InterestDelete.as_view(), name='delete'),
    path('<int:pk>/', InterestDetailView.as_view(), name='detail'),
    path('', InterestListView.as_view(), name='list'),
    path('find-user/', never_cache(FindSimilarUser.as_view()), name='find-user'),
    path('user-found/', never_cache(FoundSimilarUserView.as_view()), name='user-found'),
    path('deny-user/', never_cache(DenySimilarUserView.as_view()), name='deny-user'),
    path('approve-user/', never_cache(ApproveSimilarUserView.as_view()), name='approve-user'),
    path('toggle-interest/<int:pk>/', ToggleInterestView.as_view(), name='toggle-interest'),
    path('<int:pk>/comments/', InterestCommentsListView.as_view(), name='comments'),
]
