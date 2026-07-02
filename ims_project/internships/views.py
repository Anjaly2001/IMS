from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import InternshipRecord, MentorAssignment
from .forms import (
    InternshipDocumentUploadForm,
    InternshipRecordForm,
    MentorAssignmentForm,
    StudentInternshipSubmissionForm,
    VerificationForm,
)
from students.models import Student
from accounts.decorators import not_student, admin_required, faculty_required, coordinator_required
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
    record = get_object_or_404(
        InternshipRecord.objects.select_related('student', 'organisation', 'verified_by'),
        pk=pk
    )
    is_owner = False
    if request.user.is_student_role:
        try:
            is_owner = record.student == request.user.student_profile
            if not is_owner:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
        except Exception:
            return redirect('dashboard')

    has_marks = hasattr(record, 'marks')
    has_required_docs = bool(record.certificate and record.report)
    can_enter_marks = (
        not request.user.is_student_role
        and request.user.role in ('evaluator', 'faculty_mentor')
        and record.verification_status == 'verified'
        and has_required_docs
        and not has_marks
    )
    if request.user.is_admin and record.verification_status == 'verified' and has_required_docs and not has_marks:
        can_enter_marks = True

    context = {
        'record': record,
        'can_student_edit': is_owner and record.verification_status in ('draft', 'needs_correction'),
        'can_upload_documents': (
            (is_owner or request.user.is_admin)
            and record.verification_status in ('verified', 'marks_entered', 'approved')
            and record.verification_status != 'locked'
        ),
        'can_verify_internship': request.user.is_authenticated and (
            request.user.is_admin or request.user.role == 'faculty_mentor'
        ),
        'can_enter_marks': can_enter_marks,
        'can_continue_marks': (
            has_marks
            and not request.user.is_student_role
            and (request.user.is_admin or request.user.role in ('evaluator', 'faculty_mentor'))
            and record.verification_status == 'verified'
            and getattr(record, 'marks', None).status == 'draft'
        ),
        'can_review_marks': has_marks and request.user.is_admin,
    }
    return render(request, 'internships/internship_detail.html', context)

@login_required
def internship_create(request):
    if request.user.is_student_role:
        try:
            student = request.user.student_profile
        except Exception:
            messages.error(request, 'Student profile not found.')
            return redirect('dashboard')

        form = StudentInternshipSubmissionForm(
            request.POST or None,
            request.FILES or None,
            student=student,
        )
        if request.method == 'POST' and form.is_valid():
            record = form.save(commit=False)
            record.student = student
            record.verification_status = 'submitted'
            record.completion_status = 'pending'
            record.save()
            ActivityLog.objects.create(
                user=request.user,
                action='Student submitted internship details',
                module='Internships',
                record_id=str(record.pk),
            )
            messages.success(request, 'Internship details submitted for faculty review.')
            return redirect('internship_detail', pk=record.pk)
        return render(request, 'internships/internship_form.html', {
            'form': form,
            'title': 'Submit Internship Details',
            'is_student_submission': True,
        })

    student_id = request.GET.get('student')
    initial = {}
    if student_id:
        initial['student'] = student_id
    form = InternshipRecordForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False)
        # Two distinct actions per SRS: "Save Draft" leaves the record in
        # draft status for later completion; "Submit" sends it for
        # Faculty Coordinator verification straight away.
        if 'save_draft' in request.POST:
            record.verification_status = 'draft'
            action_label = 'Saved internship record as draft'
            success_msg = 'Internship saved as draft.'
        else:
            record.verification_status = 'submitted'
            action_label = 'Submitted internship record'
            success_msg = 'Internship submitted for verification.'
        record.save()
        ActivityLog.objects.create(user=request.user, action=action_label, module='Internships', record_id=str(record.pk))
        messages.success(request, success_msg)
        return redirect('internship_list')
    return render(request, 'internships/internship_form.html', {'form': form, 'title': 'Add Internship Record'})

@login_required
def internship_edit(request, pk):
    record = get_object_or_404(InternshipRecord, pk=pk)
    if record.verification_status == 'locked':
        messages.error(request, 'This record is locked and cannot be edited.')
        return redirect('internship_detail', pk=pk)

    if request.user.is_student_role:
        try:
            is_owner = record.student == request.user.student_profile
        except Exception:
            is_owner = False
        if not is_owner or record.verification_status not in ('draft', 'needs_correction'):
            messages.error(request, 'You can only edit your own draft or correction-requested submissions.')
            return redirect('internship_detail', pk=pk)
        form = StudentInternshipSubmissionForm(
            request.POST or None,
            request.FILES or None,
            instance=record,
            student=record.student,
        )
        if request.method == 'POST' and form.is_valid():
            updated = form.save(commit=False)
            updated.verification_status = 'submitted'
            updated.save()
            messages.success(request, 'Internship details resubmitted for review.')
            return redirect('internship_detail', pk=pk)
        return render(request, 'internships/internship_form.html', {
            'form': form,
            'title': 'Update Internship Details',
            'record': record,
            'is_student_submission': True,
        })

    # Per SRS: only the Faculty Coordinator can edit a record once it has
    # left draft status. Evaluators and other non-coordinator staff may
    # still edit while it's a draft (e.g. fixing a student's submission).
    if record.verification_status != 'draft' and not request.user.is_coordinator:
        messages.error(request, 'Only a Faculty Coordinator can edit a submitted internship record.')
        return redirect('internship_detail', pk=pk)
    form = InternshipRecordForm(request.POST or None, request.FILES or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Internship record updated.')
        return redirect('internship_list')
    return render(request, 'internships/internship_form.html', {'form': form, 'title': 'Edit Internship Record', 'record': record})

@login_required
@coordinator_required
def internship_verify(request, pk):
    if not (request.user.is_admin or request.user.role == 'faculty_mentor'):
        messages.error(request, 'Only a Faculty Mentor or Admin can verify internship submissions.')
        return redirect('internship_detail', pk=pk)
    record = get_object_or_404(InternshipRecord, pk=pk)
    previous_status = record.verification_status
    form = VerificationForm(request.POST or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        r = form.save(commit=False)
        r.verified_by = request.user
        r.verified_at = timezone.now()
        r.save()
        ActivityLog.objects.create(user=request.user, action=f'Verification status → {r.verification_status}', module='Internships', record_id=str(pk))

        # Email Automation Module: trigger only on the transition INTO
        # 'approved' (not every save while already approved), per SRS.
        if r.verification_status == 'approved' and previous_status != 'approved':
            from .notifications import send_organisation_thank_you
            sent = send_organisation_thank_you(r, triggered_by=request.user)
            if sent:
                messages.info(request, f'Thank-you email sent to {r.organisation.name}.')
            elif not r.organisation.email:
                messages.warning(request, f'Could not send thank-you email: {r.organisation.name} has no email on file.')

        messages.success(request, f'Status updated to: {r.get_verification_status_display()}')
        return redirect('internship_detail', pk=pk)
    return render(request, 'internships/verify_form.html', {'form': form, 'record': record})


@login_required
def internship_upload_documents(request, pk):
    record = get_object_or_404(InternshipRecord, pk=pk)
    if request.user.is_student_role:
        try:
            if record.student != request.user.student_profile:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
        except Exception:
            messages.error(request, 'Student profile not found.')
            return redirect('dashboard')
    elif not request.user.is_admin:
        messages.error(request, 'Only the student or an admin can upload internship documents.')
        return redirect('internship_detail', pk=pk)

    if record.verification_status not in ('verified', 'marks_entered', 'approved'):
        messages.error(request, 'Documents can be uploaded after faculty verification.')
        return redirect('internship_detail', pk=pk)
    if record.verification_status == 'locked':
        messages.error(request, 'This internship record is locked.')
        return redirect('internship_detail', pk=pk)

    form = InternshipDocumentUploadForm(request.POST or None, request.FILES or None, instance=record)
    if request.method == 'POST' and form.is_valid():
        form.save()
        ActivityLog.objects.create(
            user=request.user,
            action='Uploaded internship certificate/report',
            module='Internships',
            record_id=str(record.pk),
        )
        messages.success(request, 'Internship documents uploaded.')
        return redirect('internship_detail', pk=pk)
    return render(request, 'internships/document_upload_form.html', {'form': form, 'record': record})

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
