from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser to implement Role-Based Access Control (RBAC).

    Roles:
      - system_admin: Full system configuration and user management rights.
      - dept_admin: Full access to students/internships/marks/reports (no user profiles admin).
      - faculty_mentor: Tracks assigned student records, acts as a Faculty Coordinator to verify, edit, and approve marks/records.
      - evaluator: Standard faculty allowed to score marks, but cannot edit after submitting.
      - hod: Department Head, signs off on academic validations, creates permissions.
      - student: Standard student looking at their own profile and records.
    """
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
        """
        Overrides save behavior to ensure superusers always auto-align
        with the 'system_admin' role, preventing locking out of admin pages.
        """
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
        """
        Checks if user is System Admin, Department Admin, or superuser.
        Granting access to administrative functions.
        """
        return self.is_superuser or self.role in ('system_admin', 'dept_admin')

    @property
    def is_system_admin(self):
        """
        Checks if user has strict System Administrator permissions or is a Django superuser.
        """
        return self.is_superuser or self.role == 'system_admin'

    @property
    def is_faculty(self):
        """
        Checks if user belongs to faculty roles (Mentor or Evaluator).
        """
        return self.role in ('faculty_mentor', 'evaluator')

    @property
    def is_hod(self):
        """
        Checks if user has Head of Department role.
        """
        return self.role == 'hod'

    @property
    def is_coordinator(self):
        """
        Checks if user can act as a Faculty Coordinator.
        Coordinators can verify and edit internship records, edit marks,
        approve & lock records, and trigger thank-you emails.
        System Admins, HoDs, and Mentor roles all qualify as coordinators.
        """
        return self.is_admin or self.is_hod or self.role == 'faculty_mentor'

    @property
    def is_evaluator_role(self):
        """
        Checks if the user has evaluator-specific duties (marking sheets).
        """
        return self.role == 'evaluator'

    @property
    def can_approve_records(self):
        """
        Checks authorization to verify and approve internship items.
        """
        return self.is_coordinator

    @property
    def can_edit_marks_after_submission(self):
        """
        Determines if user can override evaluator marks after submission.
        """
        return self.is_coordinator

    @property
    def is_student_role(self):
        """
        Checks if the user is a genuine student user.
        """
        return self.role == 'student' and not self.is_superuser

class ActivityLog(models.Model):
    """
    Audit log system tracking modifications, logins, logouts, approvals,
    locks, and automated email operations.
    """
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
