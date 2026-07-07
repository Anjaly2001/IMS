from django.db import models
from accounts.models import User

class Programme(models.Model):
    """
    Represents an academic degree program (e.g. B.A. LL.B., B.B.A. LL.B.).
    Configures structural properties like degree duration, required internship count (e.g. 8),
    and whether a 5th-year assessment internship is mandatory.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    duration_years = models.PositiveSmallIntegerField(default=5)
    internship_count = models.PositiveSmallIntegerField(default=8)
    has_assessment_internship = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Batch(models.Model):
    """
    Represents a specific cohort of students enrolled under a Programme
    with definite start and end academic years.
    """
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='batches')
    name = models.CharField(max_length=50)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-start_year']
        unique_together = ['programme', 'name']

    def __str__(self):
        return f"{self.programme.code} - {self.name}"

class Student(models.Model):
    """
    Tracks a student's profile inside the IMS.
    Links the user account to academic features (Programme, Batch, timeline)
    and acts as the parent anchor for internship records and evaluations.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_break', 'On Break'),
        ('discontinued', 'Discontinued'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile')
    register_number = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, blank=True)
    programme = models.ForeignKey(Programme, on_delete=models.PROTECT)
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT)
    degree_start_date = models.DateField()
    degree_end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['register_number']

    def __str__(self):
        return f"{self.register_number} - {self.name}"

class BreakRecord(models.Model):
    """
    SRS 4.3 — Records academic breaks or leaves taken by the student.
    Tracks the type, duration, approval source, and any impact on their internship timeline.
    """
    BREAK_TYPE_CHOICES = [
        ('academic', 'Academic Break'),
        ('internship', 'Internship Break'),
        ('medical', 'Medical Break'),
        ('semester_gap', 'Semester Gap'),
        ('approved_leave', 'Approved Leave'),
        ('other', 'Other'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='breaks')
    break_type = models.CharField(max_length=20, choices=BREAK_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    approved_by = models.CharField(max_length=100, blank=True)
    reason = models.TextField(blank=True)
    impact_on_internship = models.TextField(blank=True)
    supporting_document = models.FileField(upload_to='break_docs/', blank=True, null=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.student.register_number} - {self.get_break_type_display()} ({self.start_date})"
