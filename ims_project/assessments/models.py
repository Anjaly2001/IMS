from django.db import models
from internships.models import InternshipRecord
from accounts.models import User

class AssessmentMark(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('locked', 'Locked'),
    ]
    
    internship_record = models.OneToOneField(InternshipRecord, on_delete=models.CASCADE, related_name='assessment_mark')
    worksheet_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    viva_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    certificate_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    ppo_marks = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, default=0.00)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    classification = models.CharField(max_length=20, default='regular')  # 'regular' or 'assessment'
    remarks = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    evaluator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marks_evaluated')
    assessment_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['internship_record']

    def save(self, *args, **kwargs):
        # Determine classification from internship_record
        if self.internship_record:
            self.classification = self.internship_record.internship_type
        
        # Auto calculate total
        t = self.worksheet_marks + self.viva_marks + self.certificate_marks
        if self.classification == 'assessment' and self.ppo_marks:
            t += self.ppo_marks
        self.total_marks = t
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.internship_record} - Total Marks: {self.total_marks}"

    @property
    def percentage(self):
        max_m = 30.0 if self.classification == 'assessment' else 100.0
        if max_m > 0:
            return round((float(self.total_marks) / max_m) * 100, 2)
        return 0

class MarkEditHistory(models.Model):
    assessment = models.ForeignKey(AssessmentMark, on_delete=models.CASCADE, related_name='edit_history')
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    old_marks = models.DecimalField(max_digits=6, decimal_places=2)
    new_marks = models.DecimalField(max_digits=6, decimal_places=2)
    reason = models.TextField(blank=True)
    edited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-edited_at']
