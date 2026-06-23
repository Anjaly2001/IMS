from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ActivityLog

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username','get_full_name','email','role','is_active']
    list_filter = ['role','is_active']
    fieldsets = UserAdmin.fieldsets + (('IMS Fields', {'fields': ('role','mobile','department','employee_id')}),)

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user','action','module','timestamp']
    readonly_fields = ['timestamp']
