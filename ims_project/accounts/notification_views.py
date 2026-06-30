from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from internships.models import InternshipRecord, MentorAssignment
from assessments.models import InternshipMarks


@login_required
def notifications(request):
    """
    Notifications page (per SRS nav: Dashboard > Notifications). Surfaces
    role-relevant pending items — there's no email inbox here, this is the
    in-system notification list referenced in FR-NT-01 to FR-NT-05.
    """
    user = request.user
    items = []

    if user.is_admin or user.is_hod:
        for r in InternshipRecord.objects.filter(verification_status='submitted').select_related('student', 'organisation')[:20]:
            items.append({
                'icon': 'bi-inbox', 'level': 'warning',
                'text': f'{r.student.name} submitted Internship #{r.internship_number} for verification.',
                'url_name': 'internship_detail', 'url_pk': r.pk,
            })
        for r in InternshipRecord.objects.filter(verification_status='marks_entered').select_related('student')[:20]:
            items.append({
                'icon': 'bi-clipboard-check', 'level': 'info',
                'text': f'Marks entered for {r.student.name} — Internship #{r.internship_number}, awaiting approval.',
                'url_name': 'internship_detail', 'url_pk': r.pk,
            })

    elif user.role == 'faculty_mentor':
        # Coordinator: their assigned students' pending verifications/approvals
        assigned_ids = MentorAssignment.objects.filter(faculty=user, effective_to__isnull=True).values_list('student_id', flat=True)
        for r in InternshipRecord.objects.filter(student_id__in=assigned_ids, verification_status='submitted').select_related('student')[:20]:
            items.append({
                'icon': 'bi-inbox', 'level': 'warning',
                'text': f'{r.student.name} submitted Internship #{r.internship_number} for verification.',
                'url_name': 'internship_detail', 'url_pk': r.pk,
            })
        for r in InternshipRecord.objects.filter(student_id__in=assigned_ids, verification_status='marks_entered').select_related('student')[:20]:
            items.append({
                'icon': 'bi-clipboard-check', 'level': 'info',
                'text': f'Marks entered for {r.student.name} — Internship #{r.internship_number}, awaiting your approval.',
                'url_name': 'internship_detail', 'url_pk': r.pk,
            })

    elif user.role == 'evaluator':
        for r in InternshipRecord.objects.filter(verification_status='verified').select_related('student')[:20]:
            items.append({
                'icon': 'bi-pencil-square', 'level': 'warning',
                'text': f'{r.student.name} — Internship #{r.internship_number} is verified and ready for marks entry.',
                'url_name': 'internship_detail', 'url_pk': r.pk,
            })

    elif user.is_student_role:
        try:
            student = user.student_profile
            for r in InternshipRecord.objects.filter(student=student, verification_status='needs_correction'):
                items.append({
                    'icon': 'bi-exclamation-triangle', 'level': 'danger',
                    'text': f'Internship #{r.internship_number} was returned for correction.',
                    'url_name': 'internship_detail', 'url_pk': r.pk,
                })
            for r in InternshipRecord.objects.filter(student=student, verification_status='locked'):
                items.append({
                    'icon': 'bi-check-circle', 'level': 'success',
                    'text': f'Final marks for Internship #{r.internship_number} have been published.',
                    'url_name': 'internship_detail', 'url_pk': r.pk,
                })
        except Exception:
            pass

    return render(request, 'accounts/notifications.html', {'items': items})
