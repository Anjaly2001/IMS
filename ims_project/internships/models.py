from django.db import models
from students.models import Student
from organisations.models import Organisation
from accounts.models import User

class InternshipRecord(models.Model):
    TYPE_CHOICES = [
        ('regular', 'Regular Internship'),
        ('assessment', 'Assessment Internship'),
        ('additional', 'Additional Internship'),
        ('repeated', 'Repeated Internship'),
    ]
    COMPLETION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('not_completed', 'Not Completed'),
        ('repeated', 'Repeated'),
    ]
    VERIFICATION_STATUS = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('needs_correction', 'Needs Correction'),
        ('verified', 'Verified'),
        ('marks_entered', 'Marks Entered'),
        ('approved', 'Approved'),
        ('locked', 'Locked'),
        ('rejected', 'Rejected'),
    ]
    MODE_CHOICES = [
        ('offline', 'Offline'),
        ('online', 'Online'),
        ('hybrid', 'Hybrid'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='internship_records')
    organisation = models.ForeignKey(Organisation, on_delete=models.PROTECT, related_name='internship_records')
    internship_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='regular')
    internship_number = models.CharField(max_length=20)
    related_semester = models.CharField(max_length=50, blank=True)
    academic_phase = models.CharField(max_length=50, blank=True)
    # Reporting Officer — captured per-internship since the same organisation
    # may assign a different officer for each placement (per SRS Add Internship page)
    reporting_officer_name = models.CharField(max_length=100, blank=True)
    reporting_officer_contact = models.CharField(max_length=20, blank=True)
    reporting_officer_email = models.EmailField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='offline')
    nature_of_work = models.TextField(blank=True)
    # Financial Details (per SRS)
    stipend_received = models.BooleanField(default=False, verbose_name='Stipend Received')
    stipend_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Student Experience (per SRS)
    student_remarks = models.TextField(blank=True, verbose_name='Student Experience / Remarks')
    certificate = models.FileField(upload_to='internship_certificates/', blank=True, null=True)
    report = models.FileField(upload_to='internship_reports/', blank=True, null=True)
    completion_status = models.CharField(max_length=20, choices=COMPLETION_STATUS, default='pending')
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='draft')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_internships')
    verified_at = models.DateTimeField(null=True, blank=True)
    # Faculty Remarks shown on the Approval Timeline — distinct from internal admin remarks
    faculty_remarks = models.TextField(blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student', 'internship_number']

    def __str__(self):
        return f"{self.student.register_number} - Internship {self.internship_number}"

    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0

    @property
    def approval_timeline(self):
        """Maps the internal verification_status onto the simple 3-stage
        timeline shown on the Internship Detail page: Submitted -> Verified
        -> Approved (per SRS)."""
        order = ['draft', 'submitted', 'needs_correction', 'verified',
                  'marks_entered', 'approved', 'locked', 'rejected']
        reached_submitted = self.verification_status in (
            'submitted', 'needs_correction', 'verified', 'marks_entered', 'approved', 'locked'
        )
        reached_verified = self.verification_status in ('verified', 'marks_entered', 'approved', 'locked')
        reached_approved = self.verification_status in ('approved', 'locked')
        return {
            'submitted': reached_submitted,
            'verified': reached_verified,
            'approved': reached_approved,
            'rejected': self.verification_status == 'rejected',
            'needs_correction': self.verification_status == 'needs_correction',
        }

class MentorAssignment(models.Model):
    LEVEL_CHOICES = [
        ('programme', 'Programme'),
        ('batch', 'Batch'),
        ('student', 'Student'),
        ('internship', 'Internship-Specific'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='mentor_assignments')
    faculty = models.ForeignKey(User, on_delete=models.PROTECT, related_name='mentor_assignments')
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    assignment_level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='student')
    related_semester = models.CharField(max_length=50, blank=True)
    internship_record = models.ForeignKey(InternshipRecord, on_delete=models.SET_NULL, null=True, blank=True)
    reason_for_change = models.TextField(blank=True)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_mentors')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-effective_from']

    def __str__(self):
        return f"{self.student} → {self.faculty} (from {self.effective_from})"

    @property
    def is_active(self):
        from django.utils import timezone
        today = timezone.now().date()
        if self.effective_to:
            return self.effective_from <= today <= self.effective_to
        return self.effective_from <= today
