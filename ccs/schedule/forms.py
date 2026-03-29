from django import forms
from django.contrib.auth import get_user_model

from .models import Timeslot, Activity


class TimeslotCreateForm(forms.ModelForm):
    field_order = ['start', 'end', 'activity_name', 'medium', 'location', 'notes', 'proposed_to']

    activity_name = forms.CharField(max_length=255, label='Activity')
    notes         = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Notes',
    )
    proposed_to = forms.ModelChoiceField(
        queryset=None,  # set in __init__
        label='Propose to',
    )

    class Meta:
        model  = Timeslot
        fields = ['start', 'end', 'medium', 'location']
        widgets = {
            'start': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            ),
            'end': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, requester=None, **kwargs):
        super().__init__(*args, **kwargs)
        User = get_user_model()
        is_admin = requester and (requester.is_superuser or requester.role == User.Role.ADMIN)
        if is_admin:
            qs = User.objects.filter(
                status=User.Status.ACTIVE,
                role=User.Role.USER,
            ).order_by('name', 'email')
        else:
            qs = User.objects.filter(
                status=User.Status.ACTIVE,
                role__in=[User.Role.ADMIN, User.Role.CCT],
            ).order_by('name', 'email')
        self.fields['proposed_to'].queryset = qs
        self.fields['location'].required = False

    def clean(self):
        cleaned_data = super().clean()
        if (cleaned_data.get('medium') == Timeslot.Medium.IN_PERSON
                and not cleaned_data.get('location', '').strip()):
            self.add_error('location', 'Location is required for in-person meetings.')
        return cleaned_data
