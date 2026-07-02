import re

from django import forms
from .models import Student, BreakRecord, Programme, Batch

class ProgrammeForm(forms.ModelForm):
    class Meta:
        model = Programme
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-control'

    def clean_code(self):
        return self.cleaned_data['code'].strip().upper()

    def clean_name(self):
        return self.cleaned_data['name'].strip()

    def clean(self):
        cleaned_data = super().clean()
        duration_years = cleaned_data.get('duration_years')
        internship_count = cleaned_data.get('internship_count')

        if duration_years is not None and not 1 <= duration_years <= 10:
            self.add_error('duration_years', 'Duration must be between 1 and 10 years.')
        if internship_count is not None and not 1 <= internship_count <= 20:
            self.add_error('internship_count', 'Internship count must be between 1 and 20.')
        return cleaned_data

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-control'

    def clean_name(self):
        return self.cleaned_data['name'].strip()

    def clean(self):
        cleaned_data = super().clean()
        programme = cleaned_data.get('programme')
        start_year = cleaned_data.get('start_year')
        end_year = cleaned_data.get('end_year')

        if start_year and end_year:
            if end_year <= start_year:
                self.add_error('end_year', 'End year must be after start year.')
            if programme and end_year - start_year != programme.duration_years:
                self.add_error(
                    'end_year',
                    f'Batch duration should match the programme duration of {programme.duration_years} years.'
                )
        return cleaned_data

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['register_number','name','email','mobile','programme','batch','degree_start_date','degree_end_date','status','remarks']
        widgets = {
            'degree_start_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'degree_end_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            if not hasattr(f.widget, 'attrs') or 'class' not in f.widget.attrs:
                f.widget.attrs['class'] = 'form-control'

    def clean_register_number(self):
        value = self.cleaned_data['register_number'].strip().upper()
        if not re.fullmatch(r'[A-Z0-9][A-Z0-9/-]{2,29}', value):
            raise forms.ValidationError('Use 3-30 letters/numbers, with / or - only if needed.')
        return value

    def clean_name(self):
        value = self.cleaned_data['name'].strip()
        if len(value.split()) < 2:
            raise forms.ValidationError('Enter the student full name.')
        return value

    def clean_mobile(self):
        value = (self.cleaned_data.get('mobile') or '').strip()
        if value and not re.fullmatch(r'\+?[0-9][0-9 -]{7,18}', value):
            raise forms.ValidationError('Enter a valid mobile number.')
        return value

    def clean(self):
        cleaned_data = super().clean()
        programme = cleaned_data.get('programme')
        batch = cleaned_data.get('batch')
        start = cleaned_data.get('degree_start_date')
        end = cleaned_data.get('degree_end_date')
        status = cleaned_data.get('status')

        if programme and batch and batch.programme_id != programme.id:
            self.add_error('batch', 'Selected batch does not belong to the selected programme.')
        if start and end:
            if end <= start:
                self.add_error('degree_end_date', 'Degree end date must be after start date.')
            elif programme:
                actual_years = end.year - start.year
                if actual_years < programme.duration_years - 1:
                    self.add_error('degree_end_date', 'Degree period is too short for the selected programme.')
        if status == 'completed' and end and start and end <= start:
            self.add_error('status', 'A completed student must have a valid degree period.')
        return cleaned_data

class BreakRecordForm(forms.ModelForm):
    class Meta:
        model = BreakRecord
        fields = ['break_type','start_date','end_date','approved_by','reason','impact_on_internship','supporting_document','remarks']
        widgets = {
            'start_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'end_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
        }
    def __init__(self, *args, student=None, **kwargs):
        self.student = student
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            if 'class' not in f.widget.attrs:
                f.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        supporting_document = cleaned_data.get('supporting_document')

        if start and end:
            if end <= start:
                self.add_error('end_date', 'End date must be after start date.')
            if self.student:
                if start < self.student.degree_start_date:
                    self.add_error('start_date', 'Break cannot start before the degree start date.')
                if end > self.student.degree_end_date:
                    self.add_error('end_date', 'Break cannot end after the degree end date.')
        if supporting_document and supporting_document.size > 5 * 1024 * 1024:
            self.add_error('supporting_document', 'Upload a file smaller than 5 MB.')
        return cleaned_data
