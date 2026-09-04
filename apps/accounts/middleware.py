from django.shortcuts import redirect
from django.urls import reverse

EXEMPT_PATHS = ('/accounts/force-password-change/', '/accounts/logout/', '/static/')

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and getattr(request.user, 'must_change_password', False):
            if not request.path.startswith(EXEMPT_PATHS):
                return redirect('accounts:force_password_change')
        return self.get_response(request)