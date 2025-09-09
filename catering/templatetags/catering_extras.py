from django import template
from ..models import PerfilUsuario

register = template.Library()

@register.simple_tag
def get_user_profile(user):
    """
    Obtiene el perfil de usuario
    """
    try:
        return PerfilUsuario.objects.get(usuario=user)
    except PerfilUsuario.DoesNotExist:
        return None

@register.filter
def is_admin(user):
    """
    Verifica si el usuario es administrador
    """
    try:
        perfil = PerfilUsuario.objects.get(usuario=user)
        return perfil.es_admin()
    except PerfilUsuario.DoesNotExist:
        return user.is_superuser

@register.filter
def is_responsable(user):
    """
    Verifica si el usuario es responsable
    """
    try:
        perfil = PerfilUsuario.objects.get(usuario=user)
        return perfil.es_responsable()
    except PerfilUsuario.DoesNotExist:
        return False

@register.filter
def is_empleado(user):
    """
    Verifica si el usuario es empleado
    """
    try:
        perfil = PerfilUsuario.objects.get(usuario=user)
        return perfil.es_empleado()
    except PerfilUsuario.DoesNotExist:
        return False

@register.filter
def is_cliente(user):
    """
    Verifica si el usuario es cliente
    """
    try:
        perfil = PerfilUsuario.objects.get(usuario=user)
        return perfil.tipo_usuario == 'CLIENTE'
    except PerfilUsuario.DoesNotExist:
        return False
