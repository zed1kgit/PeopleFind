from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.urls import reverse_lazy

from users.forms import UserRegisterForm, UserLoginForm, UserUpdateForm, UserForm
from users.models import User


def index(request):
    context = {
        "title": "PeopleFind",
        "nav_title": "Главная",
    }
    return render(request, 'base.html', context)


class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')

class UserLoginView(LoginView):
    form_class = UserLoginForm

class UserLogoutView(LogoutView):
    pass
