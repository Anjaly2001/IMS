from django.db import models

class Organisation(models.Model):
    ORG_TYPE_CHOICES = [
        ('advocate', 'Advocate'),
        ('law_firm', 'Law Firm'),
        ('ngo', 'NGO'),
        ('court', 'Court'),
        ('company', 'Company'),
        ('government', 'Government Office'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=200)
    organisation_type = models.CharField(max_length=20, choices=ORG_TYPE_CHOICES)
    contact_person = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    area_of_work = models.CharField(max_length=200, blank=True)
    feedback_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_organisation_type_display()})"

    @property
    def student_count(self):
        return self.internship_records.count()
