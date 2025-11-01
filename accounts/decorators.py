from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """
    Decorador que verifica que el usuario sea administrador.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('accounts:login')
        
        if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
            messages.error(request, 'No tienes permisos para acceder a esta página.')
            return redirect('dashboard:dashboard')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view
