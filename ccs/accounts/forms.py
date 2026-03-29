from django import forms
from django.contrib.auth import get_user_model


class LoginForm(forms.Form):
    email    = forms.EmailField(
        widget=forms.EmailInput(attrs={'autofocus': True, 'autocomplete': 'email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
    )


class InviteForm(forms.Form):
    name  = forms.CharField(max_length=150)
    email = forms.EmailField()


class RegisterForm(forms.Form):
    name             = forms.CharField(max_length=150)
    password         = forms.CharField(widget=forms.PasswordInput, label='Password')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirm password')

    def clean(self):
        cleaned_data = super().clean()
        pw  = cleaned_data.get('password')
        pw2 = cleaned_data.get('password_confirm')
        if pw and pw2 and pw != pw2:
            self.add_error('password_confirm', 'Passwords do not match.')
        return cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model  = None   # set at runtime via get_user_model()
        fields = ['name', 'email_notifications', 'max_slot_duration']

    def __init__(self, *args, **kwargs):
        # Bind model at instantiation time to avoid import-order issues
        self.__class__.Meta.model = get_user_model()
        super().__init__(*args, **kwargs)
