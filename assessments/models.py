from django.db import models
from internships.models import Internship

class Assessment(models.Model):
    internship = models.OneToOneField(Internship, on_delete=models.CASCADE, related_name='assessment_result')
    
    # Marks (Validated in forms/clean method)
    subject_knowledge = models.DecimalField(max_digits=5, decimal_places=2, default=0) # Max 25
    practical_exposure = models.DecimalField(max_digits=5, decimal_places=2, default=0) # Max 25
    communication_skills = models.DecimalField(max_digits=5, decimal_places=2, default=0) # Max 10
    diary_maintenance = models.DecimalField(max_digits=5, decimal_places=2, default=0) # Max 40
    
    final_viva_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0) # Optional secondary evaluator
    
    feedback = models.TextField(blank=True, null=True)
    is_finalized = models.BooleanField(default=False)
    evaluated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    evaluated_at = models.DateTimeField(auto_now_add=True)
    
    # HOD Final Approval of Marks
    hod_signoff = models.BooleanField(default=False)
    hod_signoff_at = models.DateTimeField(null=True, blank=True)


    def total_marks(self):
        return self.subject_knowledge + self.practical_exposure + self.communication_skills + self.diary_maintenance

    def __str__(self):
        return f"Assessment for {self.internship}"

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('marks_entered', 'Marks Entered'),
        ('marks_updated', 'Marks Updated'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    model_name = models.CharField(max_length=50) # e.g. Assessment
    object_id = models.IntegerField()
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(null=True, blank=True) # To store before/after values
    
    def __str__(self):
        return f"{self.action} on {self.model_name} by {self.performed_by}"
