from django.db import models
from django.conf import settings

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    register_number = models.CharField(max_length=20, unique=True)
    degree_start_date = models.DateField()
    degree_end_date = models.DateField()
    batch = models.CharField(max_length=10) # e.g. 2021-2026
    current_semester = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.register_number})"

class StudentBreak(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='breaks')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    
    def __str__(self):
        return f"Break for {self.student.register_number}: {self.start_date} to {self.end_date}"

class MentorAssignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='mentor_history')
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentee_history')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.mentor.get_full_name()} -> {self.student.register_number}"
