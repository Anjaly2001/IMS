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
