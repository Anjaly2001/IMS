from django import forms
from .models import InternshipRecord, MentorAssignment
from accounts.models import User

class InternshipRecordForm(forms.ModelForm):
    class Meta:
        model = InternshipRecord
        fields = ['student','organisation','internship_type','internship_number','related_semester','academic_phase','start_date','end_date','mode','nature_of_work','certificate','report','completion_status','remarks']
        widgets = {
            'start_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'end_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            if 'class' not in f.widget.attrs:
                f.widget.attrs['class'] = 'form-control'

class MentorAssignmentForm(forms.ModelForm):
    class Meta:
        model = MentorAssignment
        fields = ['student','faculty','effective_from','effective_to','assignment_level','related_semester','internship_record','reason_for_change','remarks']
        widgets = {
            'effective_from': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'effective_to': forms.DateInput(attrs={'type':'date','class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['faculty'].queryset = User.objects.filter(role__in=['faculty_mentor','evaluator'])
        for name, f in self.fields.items():
            if 'class' not in f.widget.attrs:
                f.widget.attrs['class'] = 'form-control'

class VerificationForm(forms.ModelForm):
    class Meta:
        model = InternshipRecord
        fields = ['verification_status','remarks']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-control'
