from django.db import models
from internships.models import InternshipRecord
from accounts.models import User

class AssessmentMark(models.Model):
    TYPE_CHOICES = [
        ('intermediate', 'Intermediate Assessment'),
        ('report', 'Report Evaluation'),
        ('presentation', 'Presentation / Review'),
        ('mentor', 'Mentor Evaluation'),
        ('viva', 'Final Viva'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('locked', 'Locked'),
    ]
    internship_record = models.ForeignKey(InternshipRecord, on_delete=models.CASCADE, related_name='assessments')
    assessment_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    assessment_name = models.CharField(max_length=100)
    maximum_marks = models.DecimalField(max_digits=6, decimal_places=2)
    marks_awarded = models.DecimalField(max_digits=6, decimal_places=2)
    weightage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    assessment_date = models.DateField(null=True, blank=True)
    evaluator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='marks_entered')
    remarks = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['internship_record', 'assessment_type']

    def __str__(self):
        return f"{self.internship_record} - {self.assessment_name}: {self.marks_awarded}/{self.maximum_marks}"

    @property
    def percentage(self):
        if self.maximum_marks > 0:
            return round(float(self.marks_awarded) / float(self.maximum_marks) * 100, 2)
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
