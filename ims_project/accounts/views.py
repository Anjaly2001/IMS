from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User, ActivityLog
from .forms import LoginForm, UserCreateForm, UserEditForm
from .decorators import admin_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
        return redirect('dashboard')
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required
@admin_required
def user_list(request):
    q = request.GET.get('q','')
    role = request.GET.get('role','')
    users = User.objects.all()
    if q:
        users = users.filter(Q(username__icontains=q)|Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(email__icontains=q))
    if role:
        users = users.filter(role=role)
    return render(request, 'accounts/user_list.html', {'users': users, 'q': q, 'role': role, 'roles': User.ROLE_CHOICES})

@login_required
@admin_required
def user_create(request):
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        ActivityLog.objects.create(user=request.user, action='Created user', module='User Management', record_id=str(user.pk), new_value=str(user))
        messages.success(request, f'User {user.username} created successfully.')
        return redirect('user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Create User'})

@login_required
@admin_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserEditForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User updated successfully.')
        return redirect('user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': f'Edit User: {user.username}'})

@login_required
def activity_log(request):
    logs = ActivityLog.objects.select_related('user').all()[:200]
    return render(request, 'accounts/activity_log.html', {'logs': logs})

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user_obj': request.user})
