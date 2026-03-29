from django.conf import settings
from django.db import models


class Announcement(models.Model):
    """A message posted by an admin on the announcement dashboard."""

    title     = models.CharField(max_length=255)
    text      = models.TextField()
    author    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='announcements'
    )
    send_mail = models.BooleanField(
        default=False,
        help_text='Send an email to all users with email notifications enabled when saved.'
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
