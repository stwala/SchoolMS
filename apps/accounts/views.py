from django.shortcuts import render

# Create your views here.
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.http import QueryDict
from .forms import LoginForm, UserCreateForm, UserUpdateForm
from .models import User
from .decorators import admin_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages

class ForcePasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/force_password_change.html'
    success_url = reverse_lazy('dashboard')  # wherever you send users after login

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.user.must_change_password = False
        self.request.user.save(update_fields=['must_change_password'])
        messages.success(self.request, 'Password updated.')
        return response

def _is_safe_redirect_url(url, user):
    """
    Check if a redirect URL is safe for the user's role.
    - Students can access /dashboard/student/*
    - Teachers can access /dashboard/teacher/* and /dashboard/student/* (their own grades)
    - Admins can access /dashboard/admin/*
    """
    if not url or not isinstance(url, str):
        return False
    
    if url.startswith('http') or url.startswith('//'):
        return False  # Prevent external redirects
    
    admin_paths = ['/dashboard/admin/', '/people/']
    teacher_paths = ['/dashboard/teacher/', '/academics/']
    student_paths = ['/dashboard/student/', '/attendance/']
    
    is_admin = user.role in ['superadmin', 'admin']
    is_teacher = user.role in ['superadmin', 'admin', 'teacher']
    
    if is_admin:
        return any(url.startswith(p) for p in admin_paths + teacher_paths + student_paths)
    elif is_teacher:
        return any(url.startswith(p) for p in teacher_paths + student_paths)
    else:  # Student or Parent
        return any(url.startswith(p) for p in student_paths)


def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        print("Authenticated:", request.user.is_authenticated)
        print("Session key:", request.session.session_key)
        print("Session data:", dict(request.session))
        messages.success(request, f'Welcome back, {user.first_name or user.username}!')
        print(f"User logged in: {user.username}")
        
        # Always redirect to the user's default dashboard based on role
        # (ignore any unsafe `next` parameter to prevent redirect loops)
        return redirect(user.get_dashboard_url())

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')

@login_required
@admin_required
def user_list(request):
    users = User.objects.all().order_by('role', 'last_name')
    return render(request, 'accounts/user_list.html', {'users': users})

@login_required
@admin_required
def user_create(request):
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User created successfully.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Create user'})

@login_required
@admin_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserUpdateForm(request.POST or None, request.FILES or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User updated.')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Update user'})

@login_required
@admin_required
def user_delete(request, pk):
    """AJAX endpoint — returns JSON."""
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def profile(request):
    form = UserUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated.')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'form': form})