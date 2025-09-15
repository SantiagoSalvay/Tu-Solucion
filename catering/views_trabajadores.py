from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Personal, Servicio, EventoSolicitado, PerfilUsuario
from .decorators import empleado_required, get_user_profile

@empleado_required
def trabajador_dashboard(request):
    """
    Dashboard específico para trabajadores
    """
    perfil = get_user_profile(request.user)

    try:
        personal = Personal.objects.get(email=request.user.email)
    except Personal.DoesNotExist:
        messages.error(request, 'No se encontró información del trabajador.')
        return redirect('catering:index')

    servicios = Servicio.objects.filter(id_personal=personal).order_by('-fecha_asignacion')

    total_servicios = servicios.count()
    servicios_activos = servicios.filter(estado__in=['ASIGNADO', 'EN_SERVICIO']).count()
    servicios_completados = servicios.filter(estado='COMPLETADO').count()

    servicios_proximos = servicios.filter(
        id_evento__fecha__gte=timezone.now().date(),
        id_evento__fecha__lte=timezone.now().date() + timedelta(days=30)
    ).order_by('id_evento__fecha', 'id_evento__hora')[:5]

    servicios_hoy = servicios.filter(
        id_evento__fecha=timezone.now().date()
    ).order_by('id_evento__hora')
    
    context = {
        'personal': personal,
        'perfil': perfil,
        'total_servicios': total_servicios,
        'servicios_activos': servicios_activos,
        'servicios_completados': servicios_completados,
        'servicios_proximos': servicios_proximos,
        'servicios_hoy': servicios_hoy,
        'servicios': servicios[:10],
    }
    
    return render(request, 'catering/trabajador_dashboard.html', context)

@empleado_required
def trabajador_servicios(request):
    """
    Lista de servicios del trabajador
    """
    try:
        personal = Personal.objects.get(email=request.user.email)
    except Personal.DoesNotExist:
        messages.error(request, 'No se encontró información del trabajador.')
        return redirect('catering:index')

    estado = request.GET.get('estado', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    servicios = Servicio.objects.filter(id_personal=personal)
    
    if estado:
        servicios = servicios.filter(estado=estado)
    if fecha_desde:
        servicios = servicios.filter(id_evento__fecha__gte=fecha_desde)
    if fecha_hasta:
        servicios = servicios.filter(id_evento__fecha__lte=fecha_hasta)
    
    servicios = servicios.order_by('-id_evento__fecha')

    estados = [('ASIGNADO', 'Asignado'), ('EN_SERVICIO', 'En Servicio'), 
               ('COMPLETADO', 'Completado'), ('CANCELADO', 'Cancelado')]
    
    context = {
        'personal': personal,
        'servicios': servicios,
        'estados': estados,
        'filtros': {
            'estado': estado,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        }
    }
    
    return render(request, 'catering/trabajador_servicios.html', context)

@empleado_required
def trabajador_servicio_detail(request, pk):
    """
    Detalle de un servicio específico del trabajador - Solo información básica
    """
    try:
        personal = Personal.objects.get(email=request.user.email)
    except Personal.DoesNotExist:
        messages.error(request, 'No se encontró información del trabajador.')
        return redirect('catering:index')
    
    servicio = get_object_or_404(Servicio, pk=pk, id_personal=personal)
    evento = servicio.id_evento

    context = {
        'servicio': servicio,
        'evento': evento,
        'personal': personal,
        'es_empleado': True,
    }
    
    return render(request, 'catering/trabajador_servicio_detail.html', context)

