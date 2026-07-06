from django.db import models
from internships.models import InternshipRecord
from accounts.models import User


class InternshipMarks(models.Model):
    """
    Marks for a single internship, using the fixed component structure
    from the SRS. There are two scoring schemes depending on internship
    type:

    Regular internships (Years 1-4, internships 1-8) — total 100:
        Worksheet  0-40
        Viva       0-40
        Certificate 0-20

    Fifth Year Assessment Internship — total 30:
        Worksheet   0-10
        Viva        0-5
        Certificate 0-5
        PPO         0-10

    Exactly one InternshipMarks row exists per InternshipRecord (OneToOne).
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('locked', 'Locked'),
    ]

    internship_record = models.OneToOneField(
        InternshipRecord, on_delete=models.CASCADE, related_name='marks'
    )

    # Regular internship components (Years 1-4)
    worksheet_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    viva_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    certificate_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Fifth Year Assessment Internship only
    ppo_marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    evaluator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='marks_entered')
    evaluated_at = models.DateField(null=True, blank=True)
    evaluator_remarks = models.TextField(blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    coordinator_remarks = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='marks_approved'
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['internship_record']
        verbose_name = 'Internship Marks'
        verbose_name_plural = 'Internship Marks'

    def __str__(self):
        return f"{self.internship_record} — Marks ({self.total}/{self.max_total})"

    @property
    def is_assessment_internship(self):
        return self.internship_record.internship_type == 'assessment'

    @property
    def max_total(self):
        """30 for the 5th-year assessment internship, 100 for everything else."""
        return 30 if self.is_assessment_internship else 100

    @property
    def max_worksheet(self):
        return 10 if self.is_assessment_internship else 40

    @property
    def max_viva(self):
        return 5 if self.is_assessment_internship else 40

    @property
    def max_certificate(self):
        return 5 if self.is_assessment_internship else 20

    @property
    def max_ppo(self):
        return 10 if self.is_assessment_internship else 0

    @property
    def total(self):
        """Auto-calculated total — sums whichever components apply."""
        parts = [self.worksheet_marks, self.viva_marks, self.certificate_marks]
        if self.is_assessment_internship:
            parts.append(self.ppo_marks)
        numeric = [float(p) for p in parts if p is not None]
        if not numeric:
            return None
        return round(sum(numeric), 2)

    @property
    def is_complete(self):
        """True once every applicable component has a value entered."""
        if self.is_assessment_internship:
            return all(v is not None for v in (self.worksheet_marks, self.viva_marks, self.certificate_marks, self.ppo_marks))
        return all(v is not None for v in (self.worksheet_marks, self.viva_marks, self.certificate_marks))

    def clean(self):
        from django.core.exceptions import ValidationError
        errors = {}
        if self.worksheet_marks is not None and self.worksheet_marks > self.max_worksheet:
            errors['worksheet_marks'] = f'Worksheet marks cannot exceed {self.max_worksheet}.'
        if self.viva_marks is not None and self.viva_marks > self.max_viva:
            errors['viva_marks'] = f'Viva marks cannot exceed {self.max_viva}.'
        if self.certificate_marks is not None and self.certificate_marks > self.max_certificate:
            errors['certificate_marks'] = f'Certificate marks cannot exceed {self.max_certificate}.'
        if self.is_assessment_internship and self.ppo_marks is not None and self.ppo_marks > self.max_ppo:
            errors['ppo_marks'] = f'PPO marks cannot exceed {self.max_ppo}.'
        for field in ('worksheet_marks', 'viva_marks', 'certificate_marks', 'ppo_marks'):
            value = getattr(self, field)
            if value is not None and value < 0:
                errors[field] = 'Marks cannot be negative.'
        if errors:
            raise ValidationError(errors)


class MarkEditHistory(models.Model):
    marks = models.ForeignKey(InternshipMarks, on_delete=models.CASCADE, related_name='edit_history')
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    field_changed = models.CharField(max_length=30)
    old_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    new_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    reason = models.TextField(blank=True)
    edited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-edited_at']

    def __str__(self):
        return f"{self.marks} — {self.field_changed}: {self.old_value} → {self.new_value}"


class IntermediateMark(models.Model):
    """SRS 4.7 — Intermediate assessments before the final viva."""
    TYPE_CHOICES = [
        ('intermediate', 'Intermediate Assessment'),
        ('report', 'Report Evaluation'),
        ('presentation', 'Presentation / Review'),
        ('mentor', 'Mentor Evaluation'),
        ('attendance', 'Attendance'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'), ('submitted', 'Submitted'),
        ('approved', 'Approved'), ('locked', 'Locked'),
    ]
    internship_record = models.ForeignKey(
        'internships.InternshipRecord', on_delete=models.CASCADE, related_name='intermediate_marks'
    )
    assessment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='intermediate')
    assessment_name = models.CharField(max_length=100)
    maximum_marks = models.DecimalField(max_digits=6, decimal_places=2)
    marks_awarded = models.DecimalField(max_digits=6, decimal_places=2)
    weightage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    assessment_date = models.DateField(null=True, blank=True)
    evaluator = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='intermediate_marks_entered')
    remarks = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['assessment_date', 'id']

    def __str__(self):
        return f"{self.internship_record} — {self.assessment_name}: {self.marks_awarded}/{self.maximum_marks}"

    @property
    def percentage(self):
        if self.maximum_marks and self.maximum_marks > 0:
            return round(float(self.marks_awarded) / float(self.maximum_marks) * 100, 1)
        return 0

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.marks_awarded is not None and self.maximum_marks is not None:
            if self.marks_awarded > self.maximum_marks:
                raise ValidationError({'marks_awarded': 'Marks cannot exceed maximum.'})
            if self.marks_awarded < 0:
                raise ValidationError({'marks_awarded': 'Marks cannot be negative.'})
