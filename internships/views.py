from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Internship

@login_required
def internship_list(request):
    if request.user.role == 'student':
        # Get student's internships
        from students.models import Student
        student = request.user.student_profile
        existing_internships = Internship.objects.filter(student=student)
        
        # Mapping to slots
        slots = []
        internship_map = {i.internship_type: i for i in existing_internships}
        
        for type_code, label in Internship.INTERNSHIP_TYPES:
            slots.append({
                'type_code': type_code,
                'label': label,
                'data': internship_map.get(type_code),
                'is_assessment': type_code == 'assessment'
            })
            
        return render(request, 'internships/student_internship_list.html', {
            'slots': slots,
            'student': student
        })
    
    # Staff/Admin View
    internships = Internship.objects.all()
    return render(request, 'internships/staff_internship_list.html', {'internships': internships})

