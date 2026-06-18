from django.db import models
from students.models import Student
from organisations.models import Organisation

class Internship(models.Model):
    INTERNSHIP_TYPES = [
        ('regular_1', 'Regular Internship 1'),
        ('regular_2', 'Regular Internship 2'),
        ('regular_3', 'Regular Internship 3'),
        ('regular_4', 'Regular Internship 4'),
        ('regular_5', 'Regular Internship 5'),
        ('regular_6', 'Regular Internship 6'),
        ('regular_7', 'Regular Internship 7'),
        ('regular_8', 'Regular Internship 8'),
        ('assessment', 'Assessment Internship'),
    ]
    
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('verifying', 'Pending Verification'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='internships')
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='internships')
    internship_type = models.CharField(max_length=20, choices=INTERNSHIP_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    # Faculty Mentor at the time of internship
    mentor_at_time = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    # HOD Approval
    hod_approved = models.BooleanField(default=False)
    hod_approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('student', 'internship_type') # Ensure one of each per student

    def __str__(self):
        return f"{self.student.register_number} - {self.get_internship_type_display()}"

class WeeklyDiary(models.Model):
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='diaries')
    week_number = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    reflection_summary = models.TextField()
    faculty_remarks = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Week {self.week_number} - {self.internship}"
