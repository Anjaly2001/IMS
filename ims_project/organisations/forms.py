from django import forms
from .models import Organisation

class OrganisationForm(forms.ModelForm):
    class Meta:
        model = Organisation
        fields = '__all__'
        exclude = ['created_at','updated_at']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-control'

    def clean_name(self):
        return self.cleaned_data['name'].strip()

    def clean_phone(self):
        value = (self.cleaned_data.get('phone') or '').strip()
        if value:
            compact = value.replace(' ', '').replace('-', '')
            if not compact.lstrip('+').isdigit() or not 7 <= len(compact.lstrip('+')) <= 15:
                raise forms.ValidationError('Enter a valid phone number.')
        return value

    def clean_feedback_rating(self):
        value = self.cleaned_data.get('feedback_rating')
        if value is not None and not 0 <= value <= 5:
            raise forms.ValidationError('Rating must be between 0 and 5.')
        return value

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')
        contact_person = cleaned_data.get('contact_person')
        designation = cleaned_data.get('designation')

        if contact_person and not (email or phone):
            self.add_error('email', 'Provide email or phone for the contact person.')
        if designation and not contact_person:
            self.add_error('contact_person', 'Enter the contact person for this designation.')
        return cleaned_data
