from django import forms
from .models import InternshipMarks


class InternshipMarksForm(forms.ModelForm):
    """
    Marks entry form used by Evaluators (Worksheet/Viva/Certificate, plus
    PPO for the 5th-year assessment internship). The field set and max
    values shown adapt to the internship type — set in __init__ once the
    related internship_record is known.
    """
    class Meta:
        model = InternshipMarks
        fields = ['worksheet_marks', 'viva_marks', 'certificate_marks', 'ppo_marks',
                  'evaluated_at', 'evaluator_remarks']
        widgets = {
            'evaluated_at': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, internship_record=None, **kwargs):
        super().__init__(*args, **kwargs)
        record = internship_record or (self.instance.internship_record if self.instance and self.instance.pk else None)
        is_assessment = record and record.internship_type == 'assessment'

        for name, f in self.fields.items():
            if 'class' not in f.widget.attrs:
                f.widget.attrs['class'] = 'form-control'

        if is_assessment:
            self.fields['worksheet_marks'].label = 'Worksheet Marks (0–10)'
            self.fields['viva_marks'].label = 'Viva Marks (0–5)'
            self.fields['certificate_marks'].label = 'Certificate Marks (0–5)'
            self.fields['ppo_marks'].label = 'PPO Marks (0–10)'
            self.fields['worksheet_marks'].widget.attrs.update({'max': 10, 'step': '0.5'})
            self.fields['viva_marks'].widget.attrs.update({'max': 5, 'step': '0.5'})
            self.fields['certificate_marks'].widget.attrs.update({'max': 5, 'step': '0.5'})
            self.fields['ppo_marks'].widget.attrs.update({'max': 10, 'step': '0.5'})
        else:
            self.fields['worksheet_marks'].label = 'Worksheet Marks (0–40)'
            self.fields['viva_marks'].label = 'Viva Marks (0–40)'
            self.fields['certificate_marks'].label = 'Certificate Marks (0–20)'
            self.fields['worksheet_marks'].widget.attrs.update({'max': 40, 'step': '0.5'})
            self.fields['viva_marks'].widget.attrs.update({'max': 40, 'step': '0.5'})
            self.fields['certificate_marks'].widget.attrs.update({'max': 20, 'step': '0.5'})
            # PPO doesn't apply to regular internships — hide it entirely
            del self.fields['ppo_marks']

    def clean(self):
        cleaned_data = super().clean()
        limits = {
            'worksheet_marks': self.instance.max_worksheet if self.instance else 40,
            'viva_marks': self.instance.max_viva if self.instance else 40,
            'certificate_marks': self.instance.max_certificate if self.instance else 20,
        }
        if 'ppo_marks' in self.fields:
            limits['ppo_marks'] = self.instance.max_ppo if self.instance else 10

        for field, max_value in limits.items():
            value = cleaned_data.get(field)
            if value is not None:
                if value > max_value:
                    self.add_error(field, f'Cannot exceed {max_value} marks.')
                if value < 0:
                    self.add_error(field, 'Marks cannot be negative.')
        return cleaned_data


class MarksApprovalForm(forms.ModelForm):
    """Used by the Faculty Coordinator to review, edit, approve, or lock
    marks already submitted by an Evaluator."""
    class Meta:
        model = InternshipMarks
        fields = ['worksheet_marks', 'viva_marks', 'certificate_marks', 'ppo_marks',
                  'status', 'coordinator_remarks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_assessment = self.instance and self.instance.is_assessment_internship
        for name, f in self.fields.items():
            if 'class' not in f.widget.attrs:
                f.widget.attrs['class'] = 'form-control'
        if not is_assessment and 'ppo_marks' in self.fields:
            del self.fields['ppo_marks']

    def clean(self):
        cleaned_data = super().clean()
        limits = {
            'worksheet_marks': self.instance.max_worksheet,
            'viva_marks': self.instance.max_viva,
            'certificate_marks': self.instance.max_certificate,
        }
        if 'ppo_marks' in self.fields:
            limits['ppo_marks'] = self.instance.max_ppo

        for field, max_value in limits.items():
            value = cleaned_data.get(field)
            if value is not None:
                if value > max_value:
                    self.add_error(field, f'Cannot exceed {max_value} marks.')
                if value < 0:
                    self.add_error(field, 'Marks cannot be negative.')
        return cleaned_data
