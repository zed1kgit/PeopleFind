from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import Resolver404, resolve

# Страницы, доступные пользователю с неподтвержденной почтой
EXEMPT_URL_NAMES = {'login', 'logout', 'register', 'activate'}


class EmailVerificationMiddleware:
    """Не пускает пользователей с неподтвержденной почтой дальше страницы входа.

    Проверка выполняется до view (раньше она стояла после get_response, то есть
    view успевал отработать) и не трогает вход, выход, активацию, статику и медиа.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated and not user.is_email_verified and not self._is_exempt(request):
            messages.error(request, 'Подтвердите почту по ссылке из письма.')
            return redirect('users:login')
        return self.get_response(request)

    @staticmethod
    def _is_exempt(request):
        if request.path.startswith((settings.STATIC_URL, settings.MEDIA_URL)):
            return True
        try:
            match = resolve(request.path_info)
        except Resolver404:
            return True
        return match.namespace == 'users' and match.url_name in EXEMPT_URL_NAMES
