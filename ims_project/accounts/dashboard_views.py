import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from students.models import Student
from organisations.models import Organisation
from internships.models import InternshipRecord, MentorAssignment
from assessments.models import InternshipMarks


@login_required
def dashboard(request):
    user = request.user
    context = {}

    if user.is_admin:
        context.update(_admin_dashboard_context())
    elif user.role == 'faculty_mentor':
        # Faculty Coordinator dashboard
        assigned_students = MentorAssignment.objects.filter(faculty=user, effective_to__isnull=True).values_list('student_id', flat=True)
        context.update({
            'assigned_count': len(assigned_students),
            'pending_verification': InternshipRecord.objects.filter(student_id__in=assigned_students, verification_status='submitted').count(),
            'pending_approvals': InternshipRecord.objects.filter(student_id__in=assigned_students, verification_status='marks_entered').count(),
            'my_students': Student.objects.filter(id__in=assigned_students)[:10],
        })
    elif user.role == 'evaluator':
        verified_internships = InternshipRecord.objects.filter(
            verification_status='verified'
        ).select_related('student', 'organisation')
        context.update({
            'pending_marks': verified_internships.count(),
            'marks_entered_today': InternshipMarks.objects.filter(evaluator=user).count(),
            'verified_internships': verified_internships[:10],
        })
    elif user.role == 'hod':
        total_intern = InternshipRecord.objects.count()
        completed_intern = InternshipRecord.objects.filter(completion_status='completed').count()
        context.update({
            'total_students': Student.objects.filter(status='active').count(),
            'completed_pct': round(completed_intern / max(total_intern, 1) * 100),
            'pending_approvals': InternshipRecord.objects.filter(verification_status='marks_entered').count(),
        })
    elif user.is_student_role:
        try:
            student = user.student_profile
            context.update({
                'student': student,
                'internships': InternshipRecord.objects.filter(student=student).order_by('internship_number'),
                'pending_docs': InternshipRecord.objects.filter(student=student, certificate='').count(),
                'mentor': MentorAssignment.objects.filter(student=student, effective_to__isnull=True).select_related('faculty').first(),
            })
        except Exception:
            pass

    # 'role' drives which dashboard block the template renders. A superuser
    # always sees the admin dashboard, regardless of the raw role field.
    context['role'] = 'system_admin' if user.is_admin else user.role
    return render(request, 'dashboard/index.html', context)


def _admin_dashboard_context():
    """
    Builds the KPI cards and chart data specified in the SRS Dashboard Page:

    KPI Cards
        Students:      Total Students, Active Students
        Internships:   Total Internships, Pending Verification, Approved Internships
        Marks:         Pending Marks, Completed Marks
        Organisations: Total Organisations, Active Organisations

    Charts
        Internship Completion — by academic Year 1-5
        Marks Analysis        — Average / Highest / Lowest marks
        Pending Activities    — Pending Verification / Pending Marks / Pending Approvals
    """
    all_records = InternshipRecord.objects.all()

    # --- KPI: Students ---
    total_students = Student.objects.count()
    active_students = Student.objects.filter(status='active').count()

    # --- KPI: Internships ---
    total_internships = all_records.count()
    pending_verification = all_records.filter(verification_status='submitted').count()
    approved_internships = all_records.filter(verification_status__in=['approved', 'locked']).count()

    # --- KPI: Marks ---
    verified_records = all_records.filter(verification_status__in=['verified', 'marks_entered', 'approved', 'locked'])
    pending_marks = sum(1 for r in verified_records if not hasattr(r, 'marks') or not r.marks.is_complete)
    completed_marks = InternshipMarks.objects.filter(status__in=['approved', 'locked']).count()

    # --- KPI: Organisations ---
    total_orgs = Organisation.objects.count()
    active_orgs = Organisation.objects.filter(is_active=True).count()

    # --- Chart: Internship Completion by Year (academic_phase: Year 1-5) ---
    completion_by_year = []
    for year_label in ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5']:
        year_records = all_records.filter(academic_phase=year_label)
        completion_by_year.append({
            'year': year_label,
            'completed': year_records.filter(completion_status='completed').count(),
            'total': year_records.count(),
        })

    # --- Chart: Marks Analysis (Average / Highest / Lowest) ---
    # Computed across every InternshipMarks row that has a usable total.
    all_totals = [m.total for m in InternshipMarks.objects.all() if m.total is not None]
    marks_analysis = {
        'average': round(sum(all_totals) / len(all_totals), 2) if all_totals else 0,
        'highest': max(all_totals) if all_totals else 0,
        'lowest': min(all_totals) if all_totals else 0,
    }

    # --- Chart: Pending Activities ---
    pending_activities = {
        'pending_verification': pending_verification,
        'pending_marks': pending_marks,
        'pending_approvals': all_records.filter(verification_status='marks_entered').count(),
    }

    return {
        'total_students': total_students,
        'active_students': active_students,
        'total_internships': total_internships,
        'pending_verification': pending_verification,
        'approved_internships': approved_internships,
        'pending_marks': pending_marks,
        'completed_marks': completed_marks,
        'total_orgs': total_orgs,
        'active_orgs': active_orgs,
        'completion_by_year': completion_by_year,
        'completion_by_year_json': json.dumps(completion_by_year),
        'marks_analysis': marks_analysis,
        'marks_analysis_json': json.dumps(marks_analysis),
        'pending_activities': pending_activities,
        'pending_activities_json': json.dumps(pending_activities),
        'recent_internships': all_records.select_related('student', 'organisation').order_by('-created_at')[:5],
    }
