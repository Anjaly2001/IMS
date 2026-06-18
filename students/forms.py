from django import forms

from .models import Student
from accounts.models import User

class StudentOnboardingForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Student
        fields = ['register_number', 'degree_start_date', 'degree_end_date', 'batch', 'current_semester']
        widgets = {
            'degree_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'degree_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'register_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 21BAL042'}),
            'batch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2021-2026'}),
            'current_semester': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }

    def save(self, commit=True):
        # Create user first
        user = User.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            role=User.ROLE_STUDENT
        )
        # Create student profile
        student = super().save(commit=False)
        student.user = user
        if commit:
            student.save()
        return student
