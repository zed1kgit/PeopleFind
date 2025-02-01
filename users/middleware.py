from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

class EmailVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and not request.user.is_email_verified:
            if request.path != reverse('users:login'):
                messages.error(request, 'У вас не подтверждена почта')
                return HttpResponseRedirect(reverse('users:login'))
        return response