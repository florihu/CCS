import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model. Email is the login credential.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        USER  = 'user',  'User'
        CCT   = 'cct',   'Core Care Taker'

    class Status(models.TextChoices):
        INVITED  = 'invited',  'Invited'
        ACTIVE   = 'active',   'Active'
        DISABLED = 'disabled', 'Disabled'

    email = models.EmailField(unique=True)
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']  # still needed by createsuperuser

    name   = models.CharField(max_length=150, blank=True)
    role   = models.CharField(max_length=10, choices=Role.choices,   default=Role.USER)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.INVITED)

    # Invitation
    invite_token      = models.UUIDField(default=uuid.uuid4, null=True, blank=True)
    invite_expires_at = models.DateTimeField(null=True, blank=True)

    # Preferences
    email_notifications = models.BooleanField(default=True)
    max_slot_duration   = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Recommended maximum slot duration in minutes. Overrides the global default.'
    )

    def __str__(self):
        return self.email
