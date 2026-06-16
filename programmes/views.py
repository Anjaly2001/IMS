from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def programme_list(request):
    return render(request, 'programmes/programme_list.html')
