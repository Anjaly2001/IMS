from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def assessment_list(request):
    return render(request, 'assessments/assessment_list.html')

@login_required
def viva_marking(request, student_id):
    # Mock student data for demonstration
    student_data = {
        'id': student_id,
        'name': 'Aarav Mehta' if student_id == '21BAL042' else 'Student Name',
        'reg_no': student_id,
        'organisation': 'Khaitan & Co.',
        'batch': '2021-2026',
    }
    return render(request, 'assessments/viva_marking_form.html', {'student': student_data})

@login_required
def mark_entry(request):
    return render(request, 'assessments/mark_entry.html')


