from django import forms


class LoginForm(forms.Form):
    email = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'type': 'email',
            'class': 'form-control',
            'placeholder': 'Email Address',
            'aria-describedby': 'emailHelp',
        }),
        label='Email Address',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        }),
        label='Password',
    )
    remember = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label='Remember me',
    )
