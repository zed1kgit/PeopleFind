from django.urls import path

from users.apps import UsersConfig
from users.views import index, UserRegisterView, UserLoginView, UserLogoutView, UserProfileView, SelfProfileView, \
    UserIdRedirectView, MutualUsersListView, NotificationsListView, NotificationReadView

app_name = UsersConfig.name

urlpatterns = [
    path('', index, name='index'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/<int:pk>/', UserIdRedirectView.as_view(), name='profile-id-redirect'),
    path('profile/<slug:slug>/', UserProfileView.as_view(), name='profile'),
    path('profile/', SelfProfileView.as_view(), name='profile-redirect'),
    path('mutual-users/', MutualUsersListView.as_view(), name='mutual-list'),
    path('notifications/', NotificationsListView.as_view(), name='notifications'),
    path('mark_as_read/<int:pk>/', NotificationReadView.as_view(), name='mark_as_read'),
]