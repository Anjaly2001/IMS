from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Organisation
from .forms import OrganisationForm
from accounts.decorators import not_student

@login_required
@not_student
def org_list(request):
    q = request.GET.get('q','')
    org_type = request.GET.get('type','')
    orgs = Organisation.objects.all()
    if q:
        orgs = orgs.filter(Q(name__icontains=q)|Q(city__icontains=q)|Q(area_of_work__icontains=q))
    if org_type:
        orgs = orgs.filter(organisation_type=org_type)
    return render(request, 'organisations/org_list.html', {
        'orgs': orgs, 'q': q, 'org_type': org_type,
        'types': Organisation.ORG_TYPE_CHOICES,
    })

@login_required
@not_student
def org_detail(request, pk):
    org = get_object_or_404(Organisation, pk=pk)
    internships = org.internship_records.select_related('student').order_by('-start_date')[:20]
    return render(request, 'organisations/org_detail.html', {'org': org, 'internships': internships})

@login_required
@not_student
def org_create(request):
    form = OrganisationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        org = form.save()
        messages.success(request, f'Organisation "{org.name}" added.')
        return redirect('org_list')
    return render(request, 'organisations/org_form.html', {'form': form, 'title': 'Add Organisation / Advocate'})

@login_required
@not_student
def org_edit(request, pk):
    org = get_object_or_404(Organisation, pk=pk)
    form = OrganisationForm(request.POST or None, instance=org)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Organisation updated.')
        return redirect('org_list')
    return render(request, 'organisations/org_form.html', {'form': form, 'title': f'Edit: {org.name}'})
