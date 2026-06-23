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

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-control'

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

class BreakRecordForm(forms.ModelForm):
    class Meta:
        model = BreakRecord
        fields = ['break_type','start_date','end_date','approved_by','reason','impact_on_internship','supporting_document','remarks']
        widgets = {
            'start_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'end_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            if 'class' not in f.widget.attrs:
                f.widget.attrs['class'] = 'form-control'
