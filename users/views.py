from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.views.generic import CreateView, UpdateView, ListView, DetailView, RedirectView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from Interests.models import Interest
from users.forms import UserRegisterForm, UserLoginForm, UserUpdateForm, UserForm
from users.models import User, Notification, UserRoles


def index(request):
    context = {
        "title": "PeopleFind",
        "nav_title": "Главная",
        "interests_objects_list": Interest.objects.annotate(
            related_count=Count('members')
        ).order_by('-related_count')[:4],
    }
    return render(request, 'index.html', context)


class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context


class UserLoginView(LoginView):
    form_class = UserLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация'
        return context

    def get_default_redirect_url(self):
        next_page = self.kwargs.get('next')
        if next_page:
            return next_page
        return reverse_lazy('users:index')


class UserLogoutView(LogoutView):
    pass


class UserProfileView(DetailView):
    model = User
    context_object_name = 'object'


class UserUpdateView(UpdateView):
    model = User
    form_class = UserUpdateForm

    def get_object(self, queryset=None):
        return get_object_or_404(User, slug=self.kwargs['slug'])

    def get_success_url(self):
        return reverse_lazy('users:profile', kwargs={'slug': self.kwargs['slug']})

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.is_authenticated:
            if request.user == obj or request.user.role in (UserRoles.MODERATOR, UserRoles.ADMIN,):
                return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied()


class SelfProfileView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        return reverse_lazy('users:profile', kwargs={'slug': user.slug})


class UserIdRedirectView(RedirectView):
    model = User

    def get_redirect_url(self, *args, **kwargs):
        user_slug = User.objects.get(pk=self.kwargs['pk']).slug
        return reverse_lazy('users:profile', kwargs={'slug': user_slug})


class MutualUsersListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/mutual_users_list.html'

    def get_queryset(self):
        user = self.request.user
        approved_users = user.approved_users.all()
        mutual_users = []
        for approved_user in approved_users:
            if approved_user.approved_users.all().contains(user):
                mutual_users.append(approved_user)
        return mutual_users


class NotificationsListView(LoginRequiredMixin, ListView):
    model = Notification

    def get_queryset(self):
        return self.request.user.notifications.all().order_by('-date_created')


class NotificationReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        notification = Notification.objects.get(id=kwargs.get('pk'), user=self.request.user)
        notification.viewed = True
        notification.save()
        return JsonResponse({'success': True})