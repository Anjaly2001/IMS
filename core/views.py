from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def home(request):
    """Home page - redirect authenticated users to their role dashboard."""
    if request.user.is_authenticated:
        from accounts.views import _role_redirect
        return _role_redirect(request.user)
    return render(request, 'core/home.html')


@login_required
def admin_dashboard(request):
    """Admin dashboard with key metrics."""
    from django.apps import apps
    from accounts.models import User

    def _model_count_by_name(name):
        name = name.lower()
        for model in apps.get_models():
            if model.__name__.lower() == name:
                try:
                    return model.objects.count()
                except Exception:
                    return 0
        return 0

    total_students = User.objects.filter(role='student').count()
    total_internships = _model_count_by_name('Internship')
    pending_verifications = _model_count_by_name('Verification') or 0
    pending_marks = _model_count_by_name('Marks') or 0
    organisations = _model_count_by_name('Organisation') or _model_count_by_name('Organization')
    reports = _model_count_by_name('Report')

    context = {
        'total_students': total_students,
        'total_internships': total_internships,
        'pending_verifications': pending_verifications,
        'pending_marks': pending_marks,
        'organisations': organisations,
        'reports': reports,
    }
    return render(request, 'core/dashboards/admin_dashboard.html', context)


@login_required
def department_dashboard(request):
    """Department Admin dashboard."""
    return render(request, 'core/dashboards/department_dashboard.html')


@login_required
def mentor_dashboard(request):
    """Faculty Mentor dashboard."""
    return render(request, 'core/dashboards/mentor_dashboard.html')


@login_required
def evaluator_dashboard(request):
    """Evaluator dashboard."""
    return render(request, 'core/dashboards/evaluator_dashboard.html')


@login_required
def hod_dashboard(request):
    """HoD dashboard."""
    return render(request, 'core/dashboards/hod_dashboard.html')


@login_required
def student_dashboard(request):
    """Student dashboard."""
    return render(request, 'core/dashboards/student_dashboard.html')

