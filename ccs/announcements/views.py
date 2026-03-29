from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone

from accounts.decorators import admin_required
from .forms import AnnouncementForm
from .models import Announcement


@login_required
def announcement_list(request):
    now = timezone.now()
    announcements = Announcement.objects.filter(is_active=True).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gte=now)
    ).order_by('-created_at')
    return render(request, 'announcements/list.html', {'announcements': announcements})


@login_required
@admin_required
def announcement_create(request):
    form = AnnouncementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        announcement        = form.save(commit=False)
        announcement.author = request.user
        announcement.save()
        messages.success(request, 'Announcement posted.')
        return redirect('announcements:list')
    return render(request, 'announcements/create.html', {'form': form})
