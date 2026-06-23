from django import forms
from .models import AssessmentMark

class AssessmentMarkForm(forms.ModelForm):
    class Meta:
        model = AssessmentMark
        fields = ['assessment_type','assessment_name','maximum_marks','marks_awarded','weightage','assessment_date','remarks']
        widgets = {
            'assessment_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            if 'class' not in f.widget.attrs:
                f.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        max_marks = cleaned_data.get('maximum_marks')
        marks = cleaned_data.get('marks_awarded')
        if max_marks and marks:
            if marks > max_marks:
                raise forms.ValidationError("Marks awarded cannot exceed maximum marks.")
            if marks < 0:
                raise forms.ValidationError("Marks awarded cannot be negative.")
        return cleaned_data
