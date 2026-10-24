from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm, AuthenticationForm

from users.models import User
from Interests.forms import StyleFormMixin


class UserForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'name', 'slug', 'avatar', 'contacts', 'description',)


class UserAdminForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = User
        # без password: поле с хэшем нельзя править как обычный текст
        fields = ('avatar', 'email', 'name', 'slug', 'contacts', 'description',
                  'role', 'is_active', 'is_email_verified',)


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'slug', 'name', )


class UserLoginForm(StyleFormMixin, AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_email_verified:
            raise forms.ValidationError(
                'Подтвердите почту по ссылке из письма, чтобы войти.',
                code='email_not_verified',
            )


class UserUpdateForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('avatar', 'email', 'name', 'slug', 'contacts', 'description',)

class MyPasswordChangeForm(StyleFormMixin, PasswordChangeForm):
    class Meta:
        fields = ['old_password', 'new_password1', 'new_password2']
