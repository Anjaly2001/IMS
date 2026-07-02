from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Sum
from .models import InternshipMarks, MarkEditHistory
from .forms import InternshipMarksForm, MarksApprovalForm
from .calculations import calculate_student_score
from internships.models import InternshipRecord
from accounts.decorators import admin_required, not_student
from accounts.models import ActivityLog


@login_required
@not_student
def marks_entry(request, internship_pk):
    """
    Evaluator marks entry (per SRS: 'Open Student -> Enter Marks -> Submit
    -> Cannot Edit'). Creates the InternshipMarks row on first save. Once
    status has moved past 'draft', only a Coordinator can edit (handled
    by the is_locked_for_evaluator check below — see marks_review for the
    Coordinator-side edit path).
    """
    record = get_object_or_404(InternshipRecord, pk=internship_pk)
    if not (request.user.is_admin or request.user.role in ('evaluator', 'faculty_mentor')):
        messages.error(request, 'Only an Evaluator, Faculty Mentor, or Admin can enter marks.')
        return redirect('internship_detail', pk=internship_pk)
    if record.verification_status == 'locked':
        messages.error(request, 'This internship record is locked.')
        return redirect('internship_detail', pk=internship_pk)
    if record.verification_status != 'verified':
        messages.error(request, 'Marks can be entered only after the internship is verified.')
        return redirect('internship_detail', pk=internship_pk)
    if not (record.certificate and record.report):
        messages.error(request, 'Certificate and report must be uploaded before marks entry.')
        return redirect('internship_detail', pk=internship_pk)

    marks, _ = InternshipMarks.objects.get_or_create(
        internship_record=record, defaults={'evaluator': request.user}
    )

    # Evaluators cannot edit once they've submitted (per SRS). Coordinators
    # (and admins/HoD) can still come in and edit via marks_review.
    if marks.status != 'draft' and not request.user.is_coordinator:
        messages.error(request, 'These marks have been submitted and can no longer be edited. Contact your Faculty Coordinator for changes.')
        return redirect('internship_detail', pk=internship_pk)

    form = InternshipMarksForm(request.POST or None, instance=marks, internship_record=record)
    if request.method == 'POST' and form.is_valid():
        m = form.save(commit=False)
        m.evaluator = request.user
        if 'submit_marks' in request.POST:
            m.status = 'submitted'
            record.verification_status = 'marks_entered'
            record.save(update_fields=['verification_status'])
            success_msg = 'Marks submitted. You will not be able to edit them further.'
            action = 'Submitted marks'
        else:
            m.status = 'draft'
            success_msg = 'Marks saved as draft.'
            action = 'Saved marks draft'
        m.save()
        ActivityLog.objects.create(
            user=request.user, action=action, module='Assessments',
            record_id=str(m.pk), new_value=f'{m.total}/{m.max_total}'
        )
        messages.success(request, success_msg)
        return redirect('internship_detail', pk=internship_pk)

    return render(request, 'assessments/marks_entry.html', {
        'form': form, 'record': record, 'marks': marks,
        'title': 'Marks Entry',
    })


@login_required
@admin_required
def marks_review(request, pk):
    """
    Department Admin review and lock step. Admins can correct submitted
    marks if needed, then approve or lock the record for final reporting.
    """
    marks = get_object_or_404(InternshipMarks, pk=pk)
    if marks.status == 'locked':
        messages.error(request, 'These marks are locked.')
        return redirect('internship_detail', pk=marks.internship_record.pk)

    old_values = {
        'worksheet_marks': marks.worksheet_marks,
        'viva_marks': marks.viva_marks,
        'certificate_marks': marks.certificate_marks,
        'ppo_marks': marks.ppo_marks,
    }
    form = MarksApprovalForm(request.POST or None, instance=marks)
    if request.method == 'POST' and form.is_valid():
        m = form.save(commit=False)

        for field, old_value in old_values.items():
            new_value = getattr(m, field, None)
            if old_value != new_value:
                MarkEditHistory.objects.create(
                    marks=marks, edited_by=request.user, field_changed=field,
                    old_value=old_value, new_value=new_value,
                )

        if 'approve' in request.POST:
            m.status = 'approved'
            m.approved_by = request.user
            from django.utils import timezone
            m.approved_at = timezone.now()
            success_msg = 'Marks approved.'
        elif 'lock' in request.POST:
            m.status = 'locked'
            m.approved_by = request.user
            from django.utils import timezone
            m.approved_at = timezone.now()
            success_msg = 'Marks approved and locked.'
            m.internship_record.verification_status = 'locked'
            m.internship_record.save(update_fields=['verification_status'])
        else:
            success_msg = 'Marks updated.'
        m.save()

        ActivityLog.objects.create(
            user=request.user, action=f'Reviewed marks ({m.get_status_display()})',
            module='Assessments', record_id=str(m.pk),
        )
        messages.success(request, success_msg)
        return redirect('internship_detail', pk=marks.internship_record.pk)

    return render(request, 'assessments/marks_review.html', {
        'form': form, 'marks': marks, 'record': marks.internship_record,
    })


@login_required
@not_student
def marks_summary(request, student_pk):
    from students.models import Student
    student = get_object_or_404(Student, pk=student_pk)
    result = calculate_student_score(student)

    # Mark which internships' totals counted toward the "best 7"
    best7_sorted = sorted(result['best7'], reverse=True)
    used_marks_remaining = list(best7_sorted)
    data = []
    for row in result['regular_marks']:
        internship = row['internship']
        mark = row['mark']
        counted = False
        if mark is not None and mark in used_marks_remaining:
            counted = True
            used_marks_remaining.remove(mark)
        marks_obj = getattr(internship, 'marks', None)
        data.append({
            'internship': internship,
            'mark': mark,
            'marks_obj': marks_obj,
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


@login_required
@not_student
def student_score_card_pdf(request, student_pk):
    """PDF export of the score card, per SRS Reports Module (Excel/PDF export)."""
    from django.http import HttpResponse
    from students.models import Student
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet

    student = get_object_or_404(Student, pk=student_pk)
    result = calculate_student_score(student)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="score_card_{student.register_number}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph('Internship Management &amp; Assessment System', styles['Title']))
    story.append(Paragraph('Final Internship Marks — Score Card', styles['Heading3']))
    story.append(Spacer(1, 12))

    info_data = [
        ['Student Name', student.name],
        ['Register Number', student.register_number],
        ['Programme', student.programme.name],
        ['Batch', student.batch.name],
        ['Degree Period', f'{student.degree_start_date} — {student.degree_end_date}'],
    ]
    info_table = Table(info_data, colWidths=[150, 320])
    info_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph('Regular Internships — Totals out of 100 (Best 7 of 8 Considered)', styles['Heading4']))
    numbers = [row['number'] for row in result['regular_marks']]
    marks_row = [row['mark'] if row['mark'] is not None else '—' for row in result['regular_marks']]
    reg_table = Table([['#'] + numbers, ['Total'] + marks_row])
    reg_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
    ]))
    story.append(reg_table)
    story.append(Spacer(1, 16))

    calc_data = [
        ['Step 1-3: Best 7 of 8 Total / 7 = Average', f"{result['regular_avg']} / 100" if result['regular_avg'] is not None else '—'],
        ['Step 4: Average x 70 / 100 (Regular Component)', f"{result['regular_converted']} / 70" if result['regular_converted'] is not None else '—'],
        ['Step 5: Assessment Internship', f"{result['assessment_mark']} / 30" if result['assessment_mark'] is not None else 'Not entered'],
        ['Final Internship Marks', f"{result['final_score']} / 100" if result['final_score'] is not None else '—'],
    ]
    calc_table = Table(calc_data, colWidths=[320, 150])
    calc_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.whitesmoke),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    story.append(calc_table)
    story.append(Spacer(1, 12))

    status_text = 'Provisional — assessment internship pending' if result['is_provisional'] else 'Final'
    story.append(Paragraph(f'<b>Status:</b> {status_text}', styles['Normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        'Calculation: Best 7 of the 8 regular internship totals (each out of 100) are averaged, then converted '
        'to a 70-mark scale. The 5th-year Assessment Internship is scored directly out of 30. The two are added '
        'for the Final Internship Marks out of 100.', styles['Normal']
    ))

    doc.build(story)
    return response
