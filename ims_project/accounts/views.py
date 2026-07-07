from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User, ActivityLog
from .forms import LoginForm, UserCreateForm, UserEditForm
from .decorators import admin_required, system_admin_required

def _client_ip(request):
    """
    Retrieves the client's IP address from incoming request headers,
    handling reverse proxy setups (HTTP_X_FORWARDED_FOR) and falling back
    to standard remote address.
    """
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def login_view(request):
    """
    Authenticates and logs in a User. Saves User login event to Audit/ActivityLog.
    Redirects to the dashboard on successful login.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        ActivityLog.objects.create(
            user=user, action='User login', module='Authentication',
            ip_address=_client_ip(request),
        )
        messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
        return redirect('dashboard')
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    """
    Logs out the currently active User, registers the logout action in ActivityLog, Keep state clean.
    """
    ActivityLog.objects.create(
        user=request.user, action='User logout', module='Authentication',
        ip_address=_client_ip(request),
    )
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required
@system_admin_required
def user_list(request):
    """
    Renders filterable list of all user profiles in the system.
    Only system administrators can query profiles by search and filter by role.
    """
    q = request.GET.get('q','')
    role = request.GET.get('role','')
    users = User.objects.all()
    if q:
        users = users.filter(Q(username__icontains=q)|Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(email__icontains=q))
    if role:
        users = users.filter(role=role)
    return render(request, 'accounts/user_list.html', {'users': users, 'q': q, 'role': role, 'roles': User.ROLE_CHOICES})

@login_required
@system_admin_required
def user_create(request):
    """
    Permits system administrators to create new users in the database (staff accounts/mentors, etc.).
    Logs metadata creation in the ActivityLog.
    """
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        ActivityLog.objects.create(user=request.user, action='Created user', module='User Management', record_id=str(user.pk), new_value=str(user))
        messages.success(request, f'User {user.username} created successfully.')
        return redirect('user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Create User'})

@login_required
@system_admin_required
def user_edit(request, pk):
    """
    Displays form allowing system administrator to modify user roles and data.
    """
    user = get_object_or_404(User, pk=pk)
    form = UserEditForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User updated successfully.')
        return redirect('user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': f'Edit User: {user.username}'})

@login_required
def activity_log(request):
    """
    Displays the list of system activity logs for audit trails.
    """
    logs = ActivityLog.objects.select_related('user').all()[:200]
    return render(request, 'accounts/activity_log.html', {'logs': logs})

@login_required
def profile_view(request):
    """
    Displays personal information dashboard for the active user.
    """
    return render(request, 'accounts/profile.html', {'user_obj': request.user})


# ── Password Change ───────────────────────────────────────────────────────────
@login_required
def password_change_view(request):
    """
    Handles user password changes. Verifies current password and updates session hash to maintain session integrity.
    """
    from .forms import PasswordChangeCustomForm
    form = PasswordChangeCustomForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        if not request.user.check_password(form.cleaned_data['current_password']):
            form.add_error('current_password', 'Incorrect current password.')
        else:
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            ActivityLog.objects.create(user=request.user, action='Password changed', module='Authentication')
            messages.success(request, 'Password changed successfully.')
            return redirect('profile')
    return render(request, 'accounts/password_change.html', {'form': form})


# ── User CRUD additions ───────────────────────────────────────────────────────
@login_required
@system_admin_required
def user_delete(request, pk):
    """
    Handles account removal requests. Prevents self-destruction action.
    """
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('user_list')
    if request.method == 'POST':
        username = user.username
        user.delete()
        ActivityLog.objects.create(user=request.user, action=f'Deleted user: {username}', module='User Management')
        messages.success(request, f'User {username} deleted.')
        return redirect('user_list')
    return render(request, 'accounts/user_confirm_delete.html', {'user_obj': user})


@login_required
@system_admin_required
def user_toggle_active(request, pk):
    """
    Toggles is_active status of a given user. Restricts self-modification.
    """
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('user_list')
    user.is_active = not user.is_active
    user.save()
    state = 'activated' if user.is_active else 'deactivated'
    ActivityLog.objects.create(user=request.user, action=f'User {state}: {user.username}', module='User Management')
    messages.success(request, f'User {user.username} {state}.')
    return redirect('user_list')


# ── Email Settings UI ─────────────────────────────────────────────────────────
@login_required
@system_admin_required
def email_settings_view(request):
    """
    Displays current SMTP configurations read from project settings.
    Permits sending test emails to substantiate connection settings.
    """
    from django.conf import settings as dj_settings
    config = {
        'smtp_active': getattr(dj_settings, 'USE_SMTP_EMAIL', False),
        'backend': dj_settings.EMAIL_BACKEND,
        'host': getattr(dj_settings, 'EMAIL_HOST', '—'),
        'port': getattr(dj_settings, 'EMAIL_PORT', '—'),
        'use_tls': getattr(dj_settings, 'EMAIL_USE_TLS', False),
        'from_email': dj_settings.DEFAULT_FROM_EMAIL,
        'smtp_user': getattr(dj_settings, 'EMAIL_HOST_USER', '—'),
    }
    sent = None
    if request.method == 'POST':
        test_email = request.POST.get('test_email','').strip()
        if test_email:
            try:
                from django.core.mail import send_mail
                send_mail('IMS — Test Email',
                    'This is a test email from the Internship Management System.',
                    dj_settings.DEFAULT_FROM_EMAIL, [test_email])
                sent = test_email
                messages.success(request, f'Test email sent to {test_email}.')
            except Exception as e:
                messages.error(request, f'Failed: {e}')
    return render(request, 'accounts/email_settings.html', {'config': config, 'sent': sent})
