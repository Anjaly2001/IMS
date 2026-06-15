from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember = form.cleaned_data['remember']
            
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                if not remember:
                    request.session.set_expiry(0)
                return _role_redirect(user)
            else:
                form.add_error(None, 'Invalid email or password')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required(login_url='accounts:login')
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def _role_redirect(user):
    """Redirect user to appropriate dashboard based on role."""
    if user.is_superuser:
        return redirect('core:admin_dashboard')
    
    role_redirect_map = {
        'admin': 'core:admin_dashboard',
        'department_admin': 'core:department_dashboard',
        'faculty_mentor': 'core:mentor_dashboard',
        'evaluator': 'core:evaluator_dashboard',
        'hod': 'core:hod_dashboard',
        'student': 'core:student_dashboard',
    }
    
    dashboard_url = role_redirect_map.get(user.role, 'core:home')
    return redirect(dashboard_url)

