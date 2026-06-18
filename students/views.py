from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import StudentOnboardingForm

@login_required
def student_list(request):
    return render(request, 'students/student_list.html')

@login_required
def student_create(request):
    if request.method == 'POST':
        form = StudentOnboardingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('students:list')
    else:
        form = StudentOnboardingForm()
    return render(request, 'students/student_form.html', {'form': form})

