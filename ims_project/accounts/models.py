from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('system_admin', 'System Admin'),
        ('dept_admin', 'Department Admin'),
        ('faculty_mentor', 'Faculty Mentor'),
        ('evaluator', 'Evaluator'),
        ('hod', 'HoD / Programme Coordinator'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    mobile = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=30, blank=True)

    def save(self, *args, **kwargs):
        # A Django superuser (createsuperuser / is_superuser=True) always
        # counts as System Admin in the IMS role system, no matter what the
        # role field says — this guarantees superusers never get locked out
        # by role-based checks, and keeps /admin/ and the app in sync.
        if self.is_superuser and self.role != 'system_admin':
            self.role = 'system_admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        """System Admin or Department Admin — or any Django superuser."""
        return self.is_superuser or self.role in ('system_admin', 'dept_admin')

    @property
    def is_system_admin(self):
        """Full, unrestricted access — System Admin role or Django superuser."""
        return self.is_superuser or self.role == 'system_admin'

    @property
    def is_faculty(self):
        return self.role in ('faculty_mentor', 'evaluator')

    @property
    def is_hod(self):
        return self.role == 'hod'

    @property
    def is_student_role(self):
        """True only for genuine students — never true for a superuser,
        even if role happens to say 'student'."""
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
