from django import forms
from django.contrib.auth import get_user_model

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model  = Task
        fields = ['title', 'text', 'priority', 'worker', 'stored_in', 'notify_on_status_change']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        User = get_user_model()
        self.fields['worker'].queryset = User.objects.filter(
            role__in=[User.Role.CCT, User.Role.ADMIN],
            status=User.Status.ACTIVE,
        ).order_by('name', 'email')
        self.fields['worker'].required    = False
        self.fields['stored_in'].required = False
