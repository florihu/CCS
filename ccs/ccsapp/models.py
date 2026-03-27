import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model. Extends Django's built-in user with CCS-specific fields.
    We use email as the login credential instead of username.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        USER = 'user', 'User'

    class Status(models.TextChoices):
        INVITED = 'invited', 'Invited'
        ACTIVE = 'active', 'Active'
        DISABLED = 'disabled', 'Disabled'

    # Use email as the login field
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # still needed by createsuperuser

    name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.INVITED)

    # Invitation
    invite_token = models.UUIDField(default=uuid.uuid4, null=True, blank=True)
    invite_expires_at = models.DateTimeField(null=True, blank=True)

    # Preferences
    email_notifications = models.BooleanField(default=True)
    max_slot_duration = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Recommended maximum slot duration in minutes. Overrides the global default.'
    )

    def __str__(self):
        return self.email


class Timeslot(models.Model):
    """A scheduled block of time proposed to a user."""

    class Medium(models.TextChoices):
        PHONE = 'phone', 'Phone'
        VIDEO = 'video', 'Video Call'
        IN_PERSON = 'in_person', 'In Person'

    start = models.DateTimeField()
    end = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    medium = models.CharField(max_length=10, choices=Medium.choices)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_timeslots'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    has_conflict = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.start:%Y-%m-%d %H:%M} — {self.medium}'


class Activity(models.Model):
    """
    An activity proposed for a timeslot.
    Either the admin proposes it to a user, or the user suggests it to the admin.
    Both sides have an independent status field (A/B/C/D).
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        DECLINED = 'declined', 'Declined'
        ALTERNATIVE = 'alternative', 'Alternative Proposed'

    name = models.CharField(max_length=255)
    timeslot = models.ForeignKey(
        Timeslot, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='activities'
    )
    proposed_to = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='proposed_activities'
    )
    user_status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    admin_status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Set when either side chooses "D — Alternative"
    alternative_slot = models.ForeignKey(
        Timeslot, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='alternative_for'
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='suggested_activities'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} → {self.proposed_to}'

    class Meta:
        verbose_name_plural = 'Activities'


class Announcement(models.Model):
    """A message posted by an admin on the announcement dashboard."""

    title = models.CharField(max_length=255)
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='announcements'
    )
    send_mail = models.BooleanField(
        default=False,
        help_text='Send an email to all users with email notifications enabled when saved.'
    )
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class WikiEntry(models.Model):
    """A helpful link shared by an admin in the wiki section."""

    title = models.CharField(max_length=255)
    url = models.URLField()
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='wiki_entries'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Wiki Entries'
