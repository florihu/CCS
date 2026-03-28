from django import forms
from .models import User, Timeslot, Activity, Announcement, WikiEntry, Task


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'autofocus': True, 'autocomplete': 'email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
    )


class InviteForm(forms.Form):
    name = forms.CharField(max_length=150)
    email = forms.EmailField()


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirm password')

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('password')
        pw2 = cleaned_data.get('password_confirm')
        if pw and pw2 and pw != pw2:
            self.add_error('password_confirm', 'Passwords do not match.')
        return cleaned_data


class TimeslotCreateForm(forms.ModelForm):
    field_order = ['start', 'end', 'medium', 'location', 'activity_name', 'proposed_to']

    activity_name = forms.CharField(max_length=255, label='Activity')
    proposed_to = forms.ModelChoiceField(
        queryset=User.objects.none(),  # set in __init__ to avoid stale cache
        label='Propose to'
    )

    class Meta:
        model = Timeslot
        fields = ['start', 'end', 'medium', 'location']
        widgets = {
            'start': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            ),
            'end': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proposed_to'].queryset = User.objects.filter(
            status=User.Status.ACTIVE,
            role=User.Role.USER,
        ).order_by('name', 'email')
        self.fields['location'].required = False


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'text', 'expires_at', 'send_mail']
        widgets = {
            'expires_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            ),
            'text': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expires_at'].required = False


class WikiEntryForm(forms.ModelForm):
    class Meta:
        model = WikiEntry
        fields = ['title', 'url']


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'text', 'priority', 'worker', 'stored_in', 'notify_on_status_change']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['worker'].queryset = User.objects.filter(
            role__in=[User.Role.CCT, User.Role.ADMIN],
            status=User.Status.ACTIVE,
        ).order_by('name', 'email')
        self.fields['worker'].required = False
        self.fields['stored_in'].required = False


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email_notifications', 'max_slot_duration']
