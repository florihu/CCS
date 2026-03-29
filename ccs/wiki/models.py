from django.conf import settings
from django.db import models


class WikiEntry(models.Model):
    """A helpful link shared by an admin in the wiki section."""

    title      = models.CharField(max_length=255)
    url        = models.URLField()
    author     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='wiki_entries'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Wiki Entries'
