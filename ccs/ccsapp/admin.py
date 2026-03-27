from django.contrib import admin
from .models import User, Timeslot, Activity, Announcement, WikiEntry

admin.site.register(User)
admin.site.register(Timeslot)
admin.site.register(Activity)
admin.site.register(Announcement)
admin.site.register(WikiEntry)