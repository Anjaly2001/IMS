from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Sum
from .models import AssessmentMark, MarkEditHistory
from .forms import AssessmentMarkForm
from .calculations import calculate_student_score
from internships.models import InternshipRecord
from accounts.decorators import not_student
from accounts.models import ActivityLog

@login_required
@not_student
def mark_create(request, internship_pk):
    record = get_object_or_404(InternshipRecord, pk=internship_pk)
    if record.verification_status == 'locked':
        messages.error(request, 'Marks are locked for this internship.')
        return redirect('internship_detail', pk=internship_pk)
    form = AssessmentMarkForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        mark = form.save(commit=False)
        mark.internship_record = record
        mark.evaluator = request.user
        mark.save()
        # Update internship status
        record.verification_status = 'marks_entered'
        record.save(update_fields=['verification_status'])
        ActivityLog.objects.create(user=request.user, action='Entered marks', module='Assessments', record_id=str(mark.pk), new_value=f'{mark.marks_awarded}/{mark.maximum_marks}')
        messages.success(request, 'Marks saved successfully.')
        return redirect('internship_detail', pk=internship_pk)
    return render(request, 'assessments/mark_form.html', {'form': form, 'record': record, 'title': 'Add Assessment Marks'})

@login_required
@not_student
def mark_edit(request, pk):
    mark = get_object_or_404(AssessmentMark, pk=pk)
    if mark.status == 'locked':
        messages.error(request, 'These marks are locked.')
        return redirect('internship_detail', pk=mark.internship_record.pk)
    old_marks = mark.marks_awarded
    form = AssessmentMarkForm(request.POST or None, instance=mark)
    if request.method == 'POST' and form.is_valid():
        m = form.save(commit=False)
        if m.marks_awarded != old_marks:
            MarkEditHistory.objects.create(assessment=mark, edited_by=request.user, old_marks=old_marks, new_marks=m.marks_awarded)
        m.save()
        messages.success(request, 'Marks updated.')
        return redirect('internship_detail', pk=mark.internship_record.pk)
    return render(request, 'assessments/mark_form.html', {'form': form, 'mark': mark, 'title': 'Edit Marks'})

@login_required
@not_student
def mark_lock(request, pk):
    mark = get_object_or_404(AssessmentMark, pk=pk)
    if request.method == 'POST':
        mark.status = 'locked'
        mark.save()
        ActivityLog.objects.create(user=request.user, action='Locked marks', module='Assessments', record_id=str(pk))
        messages.success(request, 'Marks locked.')
    return redirect('internship_detail', pk=mark.internship_record.pk)

@login_required
@not_student
def marks_summary(request, student_pk):
    from students.models import Student
    student = get_object_or_404(Student, pk=student_pk)
    result = calculate_student_score(student)

    # Build per-internship display rows, marking which ones counted in "best 7"
    best7_sorted = sorted(result['best7'], reverse=True)
    used_marks_remaining = list(best7_sorted)  # values to "consume" as we match
    data = []
    for row in result['regular_marks']:
        internship = row['internship']
        mark = row['mark']
        intermediate = AssessmentMark.objects.filter(internship_record=internship).exclude(assessment_type='viva')
        inter_avg = intermediate.aggregate(avg=Avg('marks_awarded'))['avg']
        counted = False
        if mark is not None and mark in used_marks_remaining:
            counted = True
            used_marks_remaining.remove(mark)
        data.append({
            'internship': internship,
            'mark': mark,
            'intermediate_avg': inter_avg,
            'counted_in_best7': counted,
        })

    return render(request, 'assessments/marks_summary.html', {
        'student': student, 'data': data, 'result': result,
    })


@login_required
@not_student
def student_score_card(request, student_pk):
    """Printable/consolidated final score card for a student."""
    from students.models import Student
    student = get_object_or_404(Student, pk=student_pk)
    result = calculate_student_score(student)
    return render(request, 'assessments/score_card.html', {
        'student': student, 'result': result,
    })
