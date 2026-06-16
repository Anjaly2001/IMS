from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def student_list(request):
    return render(request, 'students/student_list.html')
