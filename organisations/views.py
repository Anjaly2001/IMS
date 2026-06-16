from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def organisation_list(request):
    return render(request, 'organisations/organisation_list.html')
