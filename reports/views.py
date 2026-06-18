from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def report_list(request):
    return render(request, 'reports/report_list.html')

@login_required
def diary_review(request, student_id):
    # Mock data for diary weeks
    weeks = [
        {'num': 1, 'status': 'Approved', 'date': 'Jan 15, 2026'},
        {'num': 2, 'status': 'Approved', 'date': 'Jan 22, 2026'},
        {'num': 3, 'status': 'Pending', 'date': 'Jan 29, 2026'},
        {'num': 4, 'status': 'Future', 'date': 'Feb 05, 2026'},
    ]
    student = {'name': 'Aarav Mehta', 'reg_no': student_id}
    return render(request, 'reports/diary_review_list.html', {'student': student, 'weeks': weeks})

@login_required
def diary_detail(request, student_id, week_num):
    student = {'name': 'Aarav Mehta', 'reg_no': student_id}
    return render(request, 'reports/diary_detail.html', {'student': student, 'week_num': week_num})

