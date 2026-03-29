import uuid
from datetime import timedelta

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .decorators import admin_required
from .forms import LoginForm, InviteForm, RegisterForm, ProfileForm

User = get_user_model()


# ── Auth ──────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['email'],
            password=form.cleaned_data['password'],
        )
        if user and (user.is_superuser or user.status == User.Status.ACTIVE):
            login(request, user)
            return redirect(request.GET.get('next', 'accounts:dashboard'))
        messages.error(request, 'Invalid email or password.')
    return render(request, 'accounts/login.html', {'form': form})


@require_POST
@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def invite_register(request, token):
    user = get_object_or_404(User, invite_token=token, status=User.Status.INVITED)
    if user.invite_expires_at and user.invite_expires_at < timezone.now():
        return render(request, 'accounts/invite/register.html', {'expired': True})
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user.name             = form.cleaned_data['name']
        user.status           = User.Status.ACTIVE
        user.invite_token     = None
        user.invite_expires_at = None
        user.set_password(form.cleaned_data['password'])
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('accounts:dashboard')
    return render(request, 'accounts/invite/register.html', {'form': form})


# ── Dashboard ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    # Import here to avoid circular imports at module load time
    from announcements.models import Announcement
    from schedule.models import Activity, Timeslot
    from tasks.models import Task

    now = timezone.now()
    active_announcements = Announcement.objects.filter(is_active=True).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gte=now)
    ).order_by('-created_at')[:3]

    ctx = {'announcements': active_announcements}

    if request.user.is_superuser or request.user.role == User.Role.ADMIN:
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

    return render(request, 'accounts/dashboard.html', ctx)


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
            user  = User(
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
            return redirect('accounts:dashboard')
    return render(request, 'accounts/invite/send.html', {'form': form})


# ── Profile ───────────────────────────────────────────────────────────────────

@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated.')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'form': form})
