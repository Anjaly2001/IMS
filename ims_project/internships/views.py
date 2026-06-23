from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import InternshipRecord, MentorAssignment
from .forms import InternshipRecordForm, MentorAssignmentForm, VerificationForm
from students.models import Student
from accounts.decorators import not_student, admin_required, faculty_required
from accounts.models import ActivityLog

@login_required
@not_student
def internship_list(request):
    q = request.GET.get('q','')
    status = request.GET.get('status','')
    vtype = request.GET.get('type','')
    records = InternshipRecord.objects.select_related('student','organisation').all()
    if request.user.role == 'faculty_mentor':
        from .models import MentorAssignment
        student_ids = MentorAssignment.objects.filter(faculty=request.user).values_list('student_id', flat=True)
        records = records.filter(student_id__in=student_ids)
    if q:
        records = records.filter(Q(student__name__icontains=q)|Q(student__register_number__icontains=q)|Q(organisation__name__icontains=q))
    if status:
        records = records.filter(verification_status=status)
    if vtype:
        records = records.filter(internship_type=vtype)
    return render(request, 'internships/internship_list.html', {
        'records': records, 'q': q, 'status': status,
        'statuses': InternshipRecord.VERIFICATION_STATUS,
        'types': InternshipRecord.TYPE_CHOICES,
    })

@login_required
def internship_detail(request, pk):
    record = get_object_or_404(InternshipRecord.objects.select_related('student','organisation','verified_by'), pk=pk)
    if request.user.is_student_role:
        try:
            if record.student != request.user.student_profile:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
        except Exception:
            return redirect('dashboard')
    assessments = record.assessments.select_related('evaluator').all()
    return render(request, 'internships/internship_detail.html', {
        'record': record, 'assessments': assessments,
    })

@login_required
@not_student
def internship_create(request):
    student_id = request.GET.get('student')
    initial = {}
    if student_id:
        initial['student'] = student_id
    form = InternshipRecordForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        record = form.save()
        ActivityLog.objects.create(user=request.user, action='Created internship record', module='Internships', record_id=str(record.pk))
        messages.success(request, 'Internship record created.')
        return redirect('internship_list')
    return render(request, 'internships/internship_form.html', {'form': form, 'title': 'Add Internship Record'})

@login_required
@not_student
def internship_edit(request, pk):
    record = get_object_or_404(InternshipRecord, pk=pk)
    if record.verification_status == 'locked':
        messages.error(request, 'This record is locked and cannot be edited.')
        return redirect('internship_detail', pk=pk)
    form = InternshipRecordForm(request.POST or None, request.FILES or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Internship record updated.')
        return redirect('internship_list')
    return render(request, 'internships/internship_form.html', {'form': form, 'title': 'Edit Internship Record', 'record': record})

@login_required
@not_student
def internship_verify(request, pk):
    record = get_object_or_404(InternshipRecord, pk=pk)
    form = VerificationForm(request.POST or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        r = form.save(commit=False)
        r.verified_by = request.user
        r.verified_at = timezone.now()
        r.save()
        ActivityLog.objects.create(user=request.user, action=f'Verification status → {r.verification_status}', module='Internships', record_id=str(pk))
        messages.success(request, f'Status updated to: {r.get_verification_status_display()}')
        return redirect('internship_detail', pk=pk)
    return render(request, 'internships/verify_form.html', {'form': form, 'record': record})

@login_required
@not_student
def mentor_assign(request, student_pk=None):
    student = None
    if student_pk:
        student = get_object_or_404(Student, pk=student_pk)
    initial = {'student': student} if student else {}
    form = MentorAssignmentForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        assignment = form.save(commit=False)
        assignment.assigned_by = request.user
        assignment.save()
        messages.success(request, 'Mentor assigned successfully.')
        return redirect('mentor_list')
    return render(request, 'internships/mentor_form.html', {'form': form, 'student': student})

@login_required
@not_student
def mentor_list(request):
    assignments = MentorAssignment.objects.select_related('student','faculty').order_by('-effective_from')
    return render(request, 'internships/mentor_list.html', {'assignments': assignments})
