from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from accounts.decorators import cct_or_admin_required
from .forms import TaskForm
from .models import Task


@login_required
@cct_or_admin_required
def task_list(request):
    tasks = Task.objects.select_related('author', 'worker').order_by(
        'status', '-priority', '-created_at'
    )
    return render(request, 'tasks/list.html', {'tasks': tasks})


@login_required
@cct_or_admin_required
def task_create(request):
    form = TaskForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        task        = form.save(commit=False)
        task.author = request.user
        task.save()
        messages.success(request, 'Task created.')
        return redirect('tasks:detail', pk=task.pk)
    return render(request, 'tasks/create.html', {'form': form})


@login_required
@cct_or_admin_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/detail.html', {'task': task})


@login_required
@cct_or_admin_required
@require_POST
def task_status_update(request, pk):
    task       = get_object_or_404(Task, pk=pk)
    new_status = request.POST.get('status')
    if new_status in Task.Status.values:
        task.status = new_status
        task.save()
        messages.success(request, f'Status updated to "{task.get_status_display()}".')
    return redirect('tasks:detail', pk=pk)
