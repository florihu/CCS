from django.conf import settings
from django.db import models


class Timeslot(models.Model):
    """A scheduled block of time proposed to a user."""

    class Medium(models.TextChoices):
        PHONE     = 'phone',     'Phone'
        VIDEO     = 'video',     'Video Call'
        IN_PERSON = 'in_person', 'In Person'

    start    = models.DateTimeField()
    end      = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    medium   = models.CharField(max_length=10, choices=Medium.choices)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_timeslots'
    )
    has_conflict = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.start:%Y-%m-%d %H:%M} — {self.medium}'


class Activity(models.Model):
    """
    An activity proposed for a timeslot.
    Either admin → user or user → admin. Both sides have an independent status.
    """

    class Status(models.TextChoices):
        PENDING     = 'pending',     'Pending'
        ACCEPTED    = 'accepted',    'Accepted'
        DECLINED    = 'declined',    'Declined'
        ALTERNATIVE = 'alternative', 'Alternative Proposed'

    name      = models.CharField(max_length=255)
    timeslot  = models.ForeignKey(
        Timeslot, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='activities'
    )
    proposed_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='proposed_activities'
    )
    user_status  = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    admin_status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    alternative_slot = models.ForeignKey(
        Timeslot, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='alternative_for'
    )
    notes = models.TextField(
        blank=True,
        help_text='Optional notes about this activity proposal.'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='suggested_activities'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} → {self.proposed_to}'

    class Meta:
        verbose_name_plural = 'Activities'
