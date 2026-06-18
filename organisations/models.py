from django.db import models

class Organisation(models.Model):
    ORG_TYPES = [
        ('law_firm', 'Law Firm'),
        ('advocate', 'Individual Advocate'),
        ('ngo', 'NGO'),
        ('corporate', 'Corporate Legal Cell'),
        ('court', 'Court/Judiciary'),
    ]
    
    name = models.CharField(max_length=255)
    org_type = models.CharField(max_length=20, choices=ORG_TYPES)
    address = models.TextField()
    contact_person = models.CharField(max_length=100) # Could be the Advocate name
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    website = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class AdvocateDetail(models.Model):
    organisation = models.OneToOneField(Organisation, on_delete=models.CASCADE, related_name='advocate_details')
    bar_council_id = models.CharField(max_length=50)
    specialization = models.CharField(max_length=200)
    years_of_experience = models.IntegerField()
    
    def __str__(self):
        return f"Adv. {self.organisation.contact_person} ({self.bar_council_id})"
