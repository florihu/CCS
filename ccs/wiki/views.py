from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required
from .forms import WikiEntryForm
from .models import WikiEntry

User = get_user_model()


@login_required
def wiki_list(request):
    entries = WikiEntry.objects.select_related('author').order_by('-created_at')
    form    = None
    if request.user.is_superuser or request.user.role == User.Role.ADMIN:
        form = WikiEntryForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            entry        = form.save(commit=False)
            entry.author = request.user
            entry.save()
            messages.success(request, 'Link added.')
            return redirect('wiki:list')
    return render(request, 'wiki/list.html', {'entries': entries, 'form': form})


@login_required
@admin_required
@require_POST
def wiki_entry_delete(request, pk):
    entry = get_object_or_404(WikiEntry, pk=pk)
    entry.delete()
    messages.success(request, 'Link removed.')
    return redirect('wiki:list')
