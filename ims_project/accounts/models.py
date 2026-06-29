from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('system_admin', 'System Admin'),
        ('faculty_coordinator', 'Faculty Coordinator'),
        ('faculty_evaluator', 'Faculty Evaluator'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='student')
    mobile = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=30, blank=True)

    def save(self, *args, **kwargs):
        if self.is_superuser and self.role != 'system_admin':
            self.role = 'system_admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        """System Admin or Faculty Coordinator — or any Django superuser."""
        return self.is_superuser or self.role in ('system_admin', 'faculty_coordinator')

    @property
    def is_system_admin(self):
        """Full, unrestricted access — System Admin role or Django superuser."""
        return self.is_superuser or self.role == 'system_admin'

    @property
    def is_coordinator(self):
        return self.is_superuser or self.role == 'faculty_coordinator'

    @property
    def is_evaluator(self):
        return self.role == 'faculty_evaluator'

    @property
    def is_faculty(self):
        return self.role in ('faculty_coordinator', 'faculty_evaluator')

    @property
    def is_student_role(self):
        return self.role == 'student' and not self.is_superuser

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    module = models.CharField(max_length=100)
    record_id = models.CharField(max_length=50, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action} [{self.timestamp:%Y-%m-%d %H:%M}]"
