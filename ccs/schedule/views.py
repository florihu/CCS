from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST


from .forms import TimeslotCreateForm
from .models import Timeslot, Activity

User = get_user_model()


@login_required
def timeslot_list(request):
    now = timezone.now()
    if request.user.is_superuser or request.user.role == User.Role.ADMIN:
        activities = Activity.objects.filter(
            timeslot__isnull=False,
            timeslot__start__gte=now,
        ).select_related('timeslot', 'proposed_to').order_by('timeslot__start')
    else:
        activities = Activity.objects.filter(
            proposed_to=request.user,
            timeslot__isnull=False,
            timeslot__start__gte=now,
        ).select_related('timeslot').order_by('timeslot__start')
    return render(request, 'schedule/list.html', {'activities': activities})


@login_required
def timeslot_create(request):
    form = TimeslotCreateForm(request.POST or None, requester=request.user)
    if request.method == 'POST' and form.is_valid():
        slot = form.save(commit=False)
        slot.created_by = request.user
        slot.save()
        Activity.objects.create(
            name=form.cleaned_data['activity_name'],
            timeslot=slot,
            proposed_to=form.cleaned_data['proposed_to'],
            notes=form.cleaned_data.get('notes', ''),
            created_by=request.user,
        )
        messages.success(request, 'Timeslot proposed.')
        return redirect('schedule:list')
    return render(request, 'schedule/create.html', {'form': form})


@login_required
def timeslot_detail(request, pk):
    slot = get_object_or_404(Timeslot, pk=pk)

    if request.user.is_superuser or request.user.role == User.Role.ADMIN:
        activity       = None
        all_activities = slot.activities.select_related('proposed_to').all()
    else:
        activity = Activity.objects.filter(
            timeslot=slot, proposed_to=request.user
        ).first()
        if not activity:
            messages.error(request, 'You do not have access to this timeslot.')
            return redirect('schedule:list')
        all_activities = None

    if request.method == 'POST' and activity:
        response = request.POST.get('response')
        if response in (Activity.Status.ACCEPTED, Activity.Status.DECLINED):
            activity.user_status = response
            activity.save()
            messages.success(request, 'Your response has been saved.')
            return redirect('schedule:detail', pk=pk)

    return render(request, 'schedule/detail.html', {
        'slot':           slot,
        'activity':       activity,
        'all_activities': all_activities,
    })
