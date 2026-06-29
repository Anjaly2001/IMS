from django import forms
from .models import AssessmentMark

class AssessmentMarkForm(forms.ModelForm):
    class Meta:
        model = AssessmentMark
        fields = ['worksheet_marks', 'viva_marks', 'certificate_marks', 'ppo_marks', 'remarks']

    def __init__(self, *args, **kwargs):
        self.internship_record = kwargs.pop('internship_record', None)
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            f.widget.attrs['class'] = 'form-control'
        
        classification = 'regular'
        if self.internship_record:
            classification = self.internship_record.internship_type
        elif self.instance and self.instance.pk:
            classification = self.instance.classification
            
        if classification == 'regular':
            if 'ppo_marks' in self.fields:
                self.fields['ppo_marks'].widget = forms.HiddenInput()
                self.fields['ppo_marks'].required = False
            self.fields['worksheet_marks'].label = "Worksheet Marks (Max 40)"
            self.fields['viva_marks'].label = "Viva Marks (Max 40)"
            self.fields['certificate_marks'].label = "Certificate Marks (Max 20)"
        else:
            self.fields['worksheet_marks'].label = "Worksheet Marks (Max 10)"
            self.fields['viva_marks'].label = "Viva Marks (Max 5)"
            self.fields['certificate_marks'].label = "Certificate Marks (Max 5)"
            if 'ppo_marks' in self.fields:
                self.fields['ppo_marks'].label = "PPO Marks (Max 10)"
                self.fields['ppo_marks'].required = True

    def clean(self):
        cleaned_data = super().clean()
        classification = 'regular'
        if self.internship_record:
            classification = self.internship_record.internship_type
        elif self.instance and self.instance.pk:
            classification = self.instance.classification

        w = cleaned_data.get('worksheet_marks', 0) or 0
        v = cleaned_data.get('viva_marks', 0) or 0
        c = cleaned_data.get('certificate_marks', 0) or 0
        p = cleaned_data.get('ppo_marks', 0) or 0

        if classification == 'regular':
            if w < 0 or w > 40:
                self.add_error('worksheet_marks', "Worksheet marks must be between 0 and 40.")
            if v < 0 or v > 40:
                self.add_error('viva_marks', "Viva marks must be between 0 and 40.")
            if c < 0 or c > 20:
                self.add_error('certificate_marks', "Certificate marks must be between 0 and 20.")
        else:
            if w < 0 or w > 10:
                self.add_error('worksheet_marks', "Worksheet marks must be between 0 and 10.")
            if v < 0 or v > 5:
                self.add_error('viva_marks', "Viva marks must be between 0 and 5.")
            if c < 0 or c > 5:
                self.add_error('certificate_marks', "Certificate marks must be between 0 and 5.")
            if p < 0 or p > 10:
                self.add_error('ppo_marks', "PPO marks must be between 0 and 10.")
        
        return cleaned_data
