from functools import wraps
from django.shortcuts import redirect


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'admin':
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def cct_or_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role not in ('admin', 'cct'):
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
