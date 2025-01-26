from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.views.generic import CreateView, UpdateView, ListView, DetailView, RedirectView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from users.forms import UserRegisterForm, UserLoginForm, UserUpdateForm, UserForm
from users.models import User


def index(request):
    context = {
        "title": "PeopleFind",
        "nav_title": "Главная",
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


class UserLogoutView(LogoutView):
    pass


class UserProfileView(DetailView):
    model = User


class SelfProfileView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        return reverse_lazy('users:profile', kwargs={'slug': user.slug})
