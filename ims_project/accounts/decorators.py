from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """System Admin, Department Admin, or Django superuser only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    return wrapper

def system_admin_required(view_func):
    """System Admin / superuser only — stricter than admin_required
    (excludes Department Admin). Used for system-wide settings."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_system_admin:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'System Administrator access required.')
        return redirect('dashboard')
    return wrapper

def faculty_required(view_func):
    """Admins, faculty mentors, evaluators, HoD — or a superuser."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        u = request.user
        if u.is_authenticated and (u.is_admin or u.is_faculty or u.is_hod):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Faculty access required.')
        return redirect('dashboard')
    return wrapper

def coordinator_required(view_func):
    """Faculty Coordinator (or admin/HoD) only — for verify, approve, lock,
    and edit-marks-after-submission actions per the SRS. Evaluators and
    Students are blocked even though they may otherwise be 'faculty'."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_coordinator:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Only a Faculty Coordinator can perform this action.')
        return redirect('dashboard')
    return wrapper

def not_student(view_func):
    """Everyone except genuine students. A superuser always passes,
    even if their role field happens to be 'student'."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_student_role:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    return wrapper
