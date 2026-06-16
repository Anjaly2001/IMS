from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def internship_list(request):
    return render(request, 'internships/internship_list.html')
