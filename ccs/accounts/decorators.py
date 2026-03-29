from functools import wraps
from django.shortcuts import redirect


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_superuser and request.user.role != 'admin':
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def cct_or_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_superuser and request.user.role not in ('admin', 'cct'):
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
