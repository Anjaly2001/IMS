from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from students.models import Student
from organisations.models import Organisation
from internships.models import InternshipRecord, MentorAssignment
from assessments.models import AssessmentMark

@login_required
def dashboard(request):
    user = request.user
    context = {}

    if user.is_admin:
        context.update({
            'total_students': Student.objects.filter(status='active').count(),
            'total_orgs': Organisation.objects.filter(is_active=True).count(),
            'completed_internships': InternshipRecord.objects.filter(completion_status='completed').count(),
            'pending_internships': InternshipRecord.objects.filter(completion_status='pending').count(),
            'pending_marks': InternshipRecord.objects.filter(verification_status='verified').exclude(assessments__assessment_type='viva').count(),
            'pending_verification': InternshipRecord.objects.filter(verification_status='submitted').count(),
            'recent_internships': InternshipRecord.objects.select_related('student','organisation').order_by('-created_at')[:5],
        })
    elif user.role == 'faculty_mentor':
        assigned_students = MentorAssignment.objects.filter(faculty=user, effective_to__isnull=True).values_list('student_id', flat=True)
        context.update({
            'assigned_count': len(assigned_students),
            'pending_verification': InternshipRecord.objects.filter(student_id__in=assigned_students, verification_status='submitted').count(),
            'my_students': Student.objects.filter(id__in=assigned_students)[:10],
        })
    elif user.role == 'evaluator':
        context.update({
            'pending_marks': InternshipRecord.objects.filter(verification_status='verified').count(),
            'marks_entered_today': AssessmentMark.objects.filter(evaluator=user).count(),
        })
    elif user.role == 'hod':
        context.update({
            'total_students': Student.objects.filter(status='active').count(),
            'completed_pct': round(InternshipRecord.objects.filter(completion_status='completed').count() / max(InternshipRecord.objects.count(), 1) * 100),
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
