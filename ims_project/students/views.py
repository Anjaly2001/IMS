from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Student, BreakRecord, Programme, Batch
from .forms import StudentForm, BreakRecordForm, ProgrammeForm, BatchForm
from accounts.decorators import admin_required, not_student
from accounts.models import User, ActivityLog

@login_required
@not_student
def student_list(request):
    q = request.GET.get('q','')
    status = request.GET.get('status','')
    programme_id = request.GET.get('programme','')
    batch_id = request.GET.get('batch','')
    students = Student.objects.select_related('programme','batch').all()
    if q:
        students = students.filter(Q(register_number__icontains=q)|Q(name__icontains=q)|Q(email__icontains=q))
    if status:
        students = students.filter(status=status)
    if programme_id:
        students = students.filter(programme_id=programme_id)
    if batch_id:
        students = students.filter(batch_id=batch_id)
    programmes = Programme.objects.filter(is_active=True)
    batches = Batch.objects.filter(is_active=True)
    return render(request, 'students/student_list.html', {
        'students': students, 'q': q, 'status': status,
        'programmes': programmes, 'batches': batches,
        'statuses': Student.STATUS_CHOICES,
    })

@login_required
def student_detail(request, pk):
    if request.user.is_student_role:
        try:
            student = request.user.student_profile
            if student.pk != pk:
                messages.error(request, 'Access denied.')
                return redirect('dashboard')
        except Exception:
            messages.error(request, 'Student profile not found.')
            return redirect('dashboard')
    student = get_object_or_404(Student.objects.select_related('programme','batch'), pk=pk)
    internships = student.internship_records.select_related('organisation').order_by('internship_number')
    breaks = student.breaks.all()
    mentors = student.mentor_assignments.select_related('faculty').order_by('-effective_from')
    from assessments.models import AssessmentMark
    from django.db.models import Avg
    viva_avg = AssessmentMark.objects.filter(
        internship_record__student=student, classification='regular'
    ).aggregate(avg=Avg('viva_marks'))['avg']
    return render(request, 'students/student_detail.html', {
        'student': student, 'internships': internships,
        'breaks': breaks, 'mentors': mentors, 'viva_avg': viva_avg,
    })

@login_required
@admin_required
def student_create(request):
    form = StudentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        student = form.save(commit=False)

        # Auto-create a User account for the student
        username = form.cleaned_data['register_number'].strip()
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=form.cleaned_data.get('email', ''),
                password=username,  # default password = register number
                first_name=form.cleaned_data['name'].split()[0] if form.cleaned_data['name'] else '',
                last_name=' '.join(form.cleaned_data['name'].split()[1:]) if len(form.cleaned_data['name'].split()) > 1 else '',
                role='student',
            )
            student.user = user
        else:
            existing_user = User.objects.get(username=username)
            student.user = existing_user

        student.save()
        ActivityLog.objects.create(user=request.user, action='Created student', module='Students', record_id=str(student.pk), new_value=str(student))
        messages.success(request, f'Student {student.name} created. Login credentials: Username = {username}, Password = {username} (default).')
        return redirect('student_list')
    return render(request, 'students/student_form.html', {'form': form, 'title': 'Add Student'})

@login_required
@admin_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Student updated successfully.')
        return redirect('student_list')
    return render(request, 'students/student_form.html', {'form': form, 'title': f'Edit: {student.name}', 'student': student})

@login_required
@not_student
def break_create(request, student_pk):
    student = get_object_or_404(Student, pk=student_pk)
    form = BreakRecordForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        br = form.save(commit=False)
        br.student = student
        if br.start_date < student.degree_start_date or br.end_date > student.degree_end_date:
            messages.error(request, 'Break dates must fall within the degree period.')
        elif br.end_date <= br.start_date:
            messages.error(request, 'End date must be after start date.')
        else:
            br.save()
            messages.success(request, 'Break record added.')
            return redirect('student_detail', pk=student_pk)
    return render(request, 'students/break_form.html', {'form': form, 'student': student})

@login_required
@not_student
def programme_list(request):
    programmes = Programme.objects.all()
    return render(request, 'students/programme_list.html', {'programmes': programmes})

@login_required
@admin_required
def programme_create(request):
    form = ProgrammeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Programme created.')
        return redirect('programme_list')
    return render(request, 'students/programme_form.html', {'form': form, 'title': 'Add Programme'})

@login_required
@not_student
def batch_list(request):
    batches = Batch.objects.select_related('programme').all()
    return render(request, 'students/batch_list.html', {'batches': batches})

@login_required
@admin_required
def batch_create(request):
    form = BatchForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Batch created.')
        return redirect('batch_list')
    return render(request, 'students/batch_form.html', {'form': form, 'title': 'Add Batch'})
