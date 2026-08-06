from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            print("Authenticated:", request.user.is_authenticated)
            print("User:", request.user)
            print("Cookies:", request.COOKIES)
            print("Session:", request.session.session_key)

            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'You do not have permission to access this page.')
            
            # Get the user's default dashboard URL (never includes next parameter)
            default_dashboard = request.user.get_dashboard_url()
            
            # If the referer is the same dashboard, return 403 to avoid redirect loop
            referer = request.META.get('HTTP_REFERER', '')
            if default_dashboard in referer:
                return HttpResponseForbidden('Access denied. You do not have permission to access this page.')
            
            return redirect(default_dashboard)
        return wrapper
    return decorator

admin_required  = role_required('superadmin', 'admin')
teacher_required = role_required('superadmin', 'admin', 'teacher')      