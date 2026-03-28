import uuid
from datetime import timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .decorators import admin_required, cct_or_admin_required
from .forms import (
    LoginForm, InviteForm, RegisterForm,
    TimeslotCreateForm, AnnouncementForm, WikiEntryForm, TaskForm, ProfileForm,
)
from .models import User, Timeslot, Activity, Announcement, WikiEntry, Task


# ── Auth ──────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
        )
        if user and (user.is_superuser or user.status == User.Status.ACTIVE):
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard'))
        messages.error(request, 'Invalid email or password.')
    return render(request, 'ccsapp/login.html', {'form': form})


@require_POST
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def invite_register(request, token):
    user = get_object_or_404(User, invite_token=token, status=User.Status.INVITED)
    if user.invite_expires_at and user.invite_expires_at < timezone.now():
        return render(request, 'ccsapp/invite/register.html', {'expired': True})
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user.name = form.cleaned_data['name']
        user.set_password(form.cleaned_data['password'])
        user.status = User.Status.ACTIVE
        user.invite_token = None
        user.invite_expires_at = None
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('dashboard')
    return render(request, 'ccsapp/invite/register.html', {'form': form})


# ── Dashboard ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    now = timezone.now()
    active_announcements = Announcement.objects.filter(is_active=True).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gte=now)
    ).order_by('-created_at')[:3]

    ctx = {'announcements': active_announcements}

    if request.user.role == User.Role.ADMIN:
        ctx['upcoming_slots'] = (
            Timeslot.objects.filter(start__gte=now).order_by('start')[:5]
        )
        ctx['conflicted_slots'] = Timeslot.objects.filter(has_conflict=True)
        ctx['open_tasks'] = Task.objects.exclude(
            status__in=[Task.Status.DONE, Task.Status.CANCELLED]
        ).select_related('worker').order_by('-priority', 'created_at')
    elif request.user.role == User.Role.CCT:
        ctx['my_slots'] = Activity.objects.filter(
            proposed_to=request.user, timeslot__start__gte=now
        ).select_related('timeslot').order_by('timeslot__start')[:5]
        ctx['my_tasks'] = Task.objects.filter(worker=request.user).exclude(
            status__in=[Task.Status.DONE, Task.Status.CANCELLED]
        )
    else:
        ctx['my_slots'] = Activity.objects.filter(
            proposed_to=request.user, timeslot__start__gte=now
        ).select_related('timeslot').order_by('timeslot__start')[:5]

    return render(request, 'ccsapp/dashboard.html', ctx)


# ── Timeslots ─────────────────────────────────────────────────────────────────

@login_required
def timeslot_list(request):
    now = timezone.now()
    if request.user.role == User.Role.ADMIN:
        slots = Timeslot.objects.filter(start__gte=now).order_by('start')
        return render(request, 'ccsapp/timeslots/list.html', {'slots': slots})
    activities = Activity.objects.filter(
        proposed_to=request.user,
        timeslot__start__gte=now,
    ).select_related('timeslot').order_by('timeslot__start')
    return render(request, 'ccsapp/timeslots/list.html', {'activities': activities})


@login_required
@admin_required
def timeslot_create(request):
    form = TimeslotCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        slot = form.save(commit=False)
        slot.created_by = request.user
        slot.save()
        Activity.objects.create(
            name=form.cleaned_data['activity_name'],
            timeslot=slot,
            proposed_to=form.cleaned_data['proposed_to'],
            created_by=request.user,
        )
        messages.success(request, 'Timeslot created and proposed.')
        return redirect('timeslot_list')
    return render(request, 'ccsapp/timeslots/create.html', {'form': form})


@login_required
def timeslot_detail(request, pk):
    slot = get_object_or_404(Timeslot, pk=pk)

    if request.user.role == User.Role.ADMIN:
        activity = None
        all_activities = slot.activities.select_related('proposed_to').all()
    else:
        activity = Activity.objects.filter(
            timeslot=slot, proposed_to=request.user
        ).first()
        if not activity:
            messages.error(request, 'You do not have access to this timeslot.')
            return redirect('timeslot_list')
        all_activities = None

    if request.method == 'POST' and activity:
        response = request.POST.get('response')
        if response in (Activity.Status.ACCEPTED, Activity.Status.DECLINED):
            activity.user_status = response
            activity.save()
            messages.success(request, 'Your response has been saved.')
            return redirect('timeslot_detail', pk=pk)

    return render(request, 'ccsapp/timeslots/detail.html', {
        'slot': slot,
        'activity': activity,
        'all_activities': all_activities,
    })


# ── Announcements ─────────────────────────────────────────────────────────────

@login_required
def announcement_list(request):
    now = timezone.now()
    announcements = Announcement.objects.filter(is_active=True).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gte=now)
    ).order_by('-created_at')
    return render(request, 'ccsapp/announcements/list.html', {
        'announcements': announcements,
    })


@login_required
@admin_required
def announcement_create(request):
    form = AnnouncementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        announcement = form.save(commit=False)
        announcement.author = request.user
        announcement.save()
        messages.success(request, 'Announcement posted.')
        return redirect('announcement_list')
    return render(request, 'ccsapp/announcements/create.html', {'form': form})


# ── Wiki ──────────────────────────────────────────────────────────────────────

@login_required
def wiki_list(request):
    entries = WikiEntry.objects.select_related('author').order_by('-created_at')
    form = None
    if request.user.role == User.Role.ADMIN:
        form = WikiEntryForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            entry = form.save(commit=False)
            entry.author = request.user
            entry.save()
            messages.success(request, 'Link added.')
            return redirect('wiki_list')
    return render(request, 'ccsapp/wiki/list.html', {'entries': entries, 'form': form})


@login_required
@admin_required
@require_POST
def wiki_entry_delete(request, pk):
    entry = get_object_or_404(WikiEntry, pk=pk)
    entry.delete()
    messages.success(request, 'Link removed.')
    return redirect('wiki_list')


# ── Tasks ─────────────────────────────────────────────────────────────────────

@login_required
@cct_or_admin_required
def task_list(request):
    tasks = Task.objects.select_related('author', 'worker').order_by(
        'status', '-priority', '-created_at'
    )
    return render(request, 'ccsapp/tasks/list.html', {'tasks': tasks})


@login_required
@cct_or_admin_required
def task_create(request):
    form = TaskForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        task.author = request.user
        task.save()
        messages.success(request, 'Task created.')
        return redirect('task_detail', pk=task.pk)
    return render(request, 'ccsapp/tasks/create.html', {'form': form})


@login_required
@cct_or_admin_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'ccsapp/tasks/detail.html', {'task': task})


@login_required
@cct_or_admin_required
@require_POST
def task_status_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    new_status = request.POST.get('status')
    if new_status in Task.Status.values:
        task.status = new_status
        task.save()
        messages.success(request, f'Status updated to "{task.get_status_display()}".')
    return redirect('task_detail', pk=pk)


# ── Invite ────────────────────────────────────────────────────────────────────

@login_required
@admin_required
def invite_send(request):
    form = InviteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email already exists.')
        else:
            token = uuid.uuid4()
            user = User(
                username=email,
                email=email,
                name=form.cleaned_data['name'],
                role=User.Role.USER,
                status=User.Status.INVITED,
                invite_token=token,
                invite_expires_at=timezone.now() + timedelta(days=7),
            )
            user.set_unusable_password()
            user.save()
            # TODO Sprint 9: send invite email via Brevo
            messages.success(
                request,
                f'Invite created for {email}. '
                f'Registration link: /invite/{token}/ — email sending not yet configured.'
            )
            return redirect('dashboard')
    return render(request, 'ccsapp/invite/send.html', {'form': form})


# ── Profile ───────────────────────────────────────────────────────────────────

@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated.')
        return redirect('profile')
    return render(request, 'ccsapp/profile.html', {'form': form})
