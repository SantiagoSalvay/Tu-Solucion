from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario

def admin_required(view_func):
    """
    Decorador que requiere que el usuario sea administrador
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            perfil = PerfilUsuario.objects.get(usuario=request.user)
            if not perfil.es_admin():
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('catering:index')
        except PerfilUsuario.DoesNotExist:

            if not request.user.is_superuser:
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('catering:index')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def empleado_required(view_func):
    """
    Decorador que requiere que el usuario sea empleado o superior
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            perfil = PerfilUsuario.objects.get(usuario=request.user)
            if not (perfil.es_admin() or perfil.es_empleado()):
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('catering:index')
        except PerfilUsuario.DoesNotExist:

            if not request.user.is_superuser:
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('catering:index')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def responsable_required(view_func):
    """
    Decorador que requiere que el usuario sea responsable (solo gestión de eventos)
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            perfil = PerfilUsuario.objects.get(usuario=request.user)
            if not perfil.es_responsable():
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('catering:index')
        except PerfilUsuario.DoesNotExist:

            if not request.user.is_superuser:
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('catering:index')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def responsable_or_admin_required(view_func):
    """
    Decorador que requiere que el usuario sea responsable o admin
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            perfil = PerfilUsuario.objects.get(usuario=request.user)
            if not (perfil.es_admin() or perfil.es_responsable()):
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('catering:index')
        except PerfilUsuario.DoesNotExist:

            if not request.user.is_superuser:
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('catering:index')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def cliente_required(view_func):
    """
    Decorador que requiere que el usuario sea cliente o superior
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            perfil = PerfilUsuario.objects.get(usuario=request.user)
            if not perfil.esta_activo():
                messages.error(request, 'Tu cuenta no está activa.')
                return redirect('catering:index')
        except PerfilUsuario.DoesNotExist:

            if not request.user.is_superuser:
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('catering:index')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def get_user_profile(user):
    """
    Función auxiliar para obtener el perfil del usuario
    """
    try:
        return PerfilUsuario.objects.get(usuario=user)
    except PerfilUsuario.DoesNotExist:
        return None
