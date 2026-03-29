from django.conf import settings
from django.db import models


class Task(models.Model):
    """
    A task visible only to Admins and CCTs (Core Care Takers).
    Can be created by either. The worker is the CCT assigned to carry it out.
    """

    class Status(models.TextChoices):
        PENDING     = 'pending',     'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        DONE        = 'done',        'Done'
        CANCELLED   = 'cancelled',   'Cancelled'

    class Priority(models.TextChoices):
        LOW    = 'low',    'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH   = 'high',   'High'

    title  = models.CharField(max_length=255)
    text   = models.TextField(help_text='Task description and necessary information.')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='authored_tasks'
    )
    status   = models.CharField(max_length=15, choices=Status.choices,  default=Status.PENDING)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    worker   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_tasks',
        help_text='The CCT assigned to carry out this task.'
    )
    stored_in = models.CharField(
        max_length=500, blank=True,
        help_text='Path or URL pointing to the server location where task input/output is stored.'
    )
    notify_on_status_change = models.BooleanField(
        default=True,
        help_text="Notify author and worker by email on status change (respects each user's email_notifications setting)."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} [{self.get_status_display()}]'
