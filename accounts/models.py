from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if not extra_fields.get("is_staff") or not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_staff=True and is_superuser=True")
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_ADMIN = "admin"
    ROLE_DEPARTMENT = "department_admin"
    ROLE_MENTOR = "faculty_mentor"
    ROLE_EVALUATOR = "evaluator"
    ROLE_HOD = "hod"
    ROLE_STUDENT = "student"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_DEPARTMENT, "Department Admin"),
        (ROLE_MENTOR, "Faculty Mentor"),
        (ROLE_EVALUATOR, "Evaluator"),
        (ROLE_HOD, "HoD"),
        (ROLE_STUDENT, "Student"),
    ]

    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, blank=True, null=True, db_index=True)
    department = models.CharField(max_length=120, blank=True, null=True, db_index=True)
    employee_id = models.CharField(max_length=60, blank=True, null=True, db_index=True)
    student_id = models.CharField(max_length=60, blank=True, null=True, db_index=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["department"]),
        ]

    def get_full_name(self):
        return (f"{self.first_name} {self.last_name}").strip()

    def get_short_name(self):
        return self.first_name or self.email

    def __str__(self):
        return self.email
