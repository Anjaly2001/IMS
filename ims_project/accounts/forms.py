from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))

class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','role','mobile','department','employee_id','password1','password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','email','role','mobile','department','employee_id','is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class PasswordChangeCustomForm(forms.Form):
    current_password = forms.CharField(label='Current Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password = forms.CharField(label='New Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))
    confirm_password = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))

    def clean_new_password(self):
        p = self.cleaned_data.get('new_password','')
        if len(p) < 8:
            raise forms.ValidationError('Password must be at least 8 characters.')
        return p

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('new_password') != cleaned.get('confirm_password'):
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned
