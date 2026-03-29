from django import forms
from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model  = Announcement
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
