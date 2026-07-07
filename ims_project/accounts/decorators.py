from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """
    Decorator for views that restrict access to System Admins, Department Admins, or Django superusers.
    Redirects non-authorized users to the dashboard with an error message.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    return wrapper

def system_admin_required(view_func):
    """
    Decorator for views that strictly restrict access to System Admins or Django superusers.
    Excludes Department Admins. Used primarily for user administration operations.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_system_admin:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'System Administrator access required.')
        return redirect('dashboard')
    return wrapper

def faculty_required(view_func):
    """
    Decorator that allows access only to System Admins, Department Admins, Faculty Mentors,
    Evaluators, HoDs, or Django superusers.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        u = request.user
        if u.is_authenticated and (u.is_admin or u.is_faculty or u.is_hod):
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Faculty access required.')
        return redirect('dashboard')
    return wrapper

def coordinator_required(view_func):
    """
    Decorator enforcing Faculty Coordinator access requirements per the SRS.
    Only Faculty Coordinators (assigned Mentor role, plus Admins and HoDs) can verify records,
    edit marks, approve & lock records, and trigger automation emails.
    Standard Evaluators and Students are denied access.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_coordinator:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Only a Faculty Coordinator can perform this action.')
        return redirect('dashboard')
    return wrapper

def not_student(view_func):
    """
    Decorator blocking access to genuine Student users.
    Allows access for all roles except standard students (a superuser always passes).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_student_role:
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    return wrapper
