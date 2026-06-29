from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q, Max, Min
from students.models import Student
from organisations.models import Organisation
from internships.models import InternshipRecord, MentorAssignment
from assessments.models import AssessmentMark

@login_required
def dashboard(request):
    user = request.user
    context = {}

    # Define roles based on properties in custom user model
    is_admin_or_coordinator = user.is_system_admin or user.is_coordinator

    if is_admin_or_coordinator:
        # KPI calculations
        total_students = Student.objects.count()
        active_students = Student.objects.filter(status='active').count()
        total_internships = InternshipRecord.objects.count()
        pending_verification = InternshipRecord.objects.filter(verification_status='submitted').count()
        approved_internships = InternshipRecord.objects.filter(verification_status='verified').count()
        
        pending_marks = InternshipRecord.objects.filter(
            verification_status='verified', assessment_mark__isnull=True
        ).count()
        completed_marks = InternshipRecord.objects.filter(
            assessment_mark__status__in=['approved', 'locked']
        ).count()
        
        total_orgs = Organisation.objects.count()
        active_orgs = Organisation.objects.filter(is_active=True).count()
        
        pending_approvals = InternshipRecord.objects.filter(
            verification_status='marks_entered'
        ).count()

        # Chart 1: Internship Completion (Completed / Locked status per year)
        # Year 1 (I1-I2), Year 2 (I3-I4), Year 3 (I5-I6), Year 4 (I7-I8), Year 5 (assessment)
        y1 = InternshipRecord.objects.filter(internship_number__in=['1', '2'], verification_status='locked').count()
        y2 = InternshipRecord.objects.filter(internship_number__in=['3', '4'], verification_status='locked').count()
        y3 = InternshipRecord.objects.filter(internship_number__in=['5', '6'], verification_status='locked').count()
        y4 = InternshipRecord.objects.filter(internship_number__in=['7', '8'], verification_status='locked').count()
        y5 = InternshipRecord.objects.filter(internship_type='assessment', verification_status='locked').count()
        
        # Chart 2: Marks Analysis (Average, Highest, Lowest out of 100 for Regular)
        marks_stats = AssessmentMark.objects.filter(classification='regular', status__in=['approved', 'locked']).aggregate(
            avg=Avg('total_marks'), max=Max('total_marks'), min=Min('total_marks')
        )
        avg_marks = float(marks_stats['avg'] or 0.0)
        max_marks = float(marks_stats['max'] or 0.0)
        min_marks = float(marks_stats['min'] or 0.0)

        context.update({
            'total_students': total_students,
            'active_students': active_students,
            'total_internships': total_internships,
            'pending_verification': pending_verification,
            'approved_internships': approved_internships,
            'pending_marks': pending_marks,
            'completed_marks': completed_marks,
            'total_orgs': total_orgs,
            'active_orgs': active_orgs,
            'pending_approvals': pending_approvals,
            'recent_internships': InternshipRecord.objects.select_related('student','organisation').order_by('-created_at')[:5],
            # Charts
            'y1': y1, 'y2': y2, 'y3': y3, 'y4': y4, 'y5': y5,
            'avg_marks': avg_marks, 'max_marks': max_marks, 'min_marks': min_marks,
        })
    elif user.is_evaluator:
        pending_marks = InternshipRecord.objects.filter(verification_status='verified', assessment_mark__isnull=True).count()
        context.update({
            'pending_marks': pending_marks,
            'marks_entered_today': AssessmentMark.objects.filter(evaluator=user).count(),
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

    context['role'] = 'system_admin' if is_admin_or_coordinator else user.role
    return render(request, 'dashboard/index.html', context)
