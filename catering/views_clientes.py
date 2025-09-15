from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import EventoSolicitado, Cliente, PerfilUsuario
from .decorators import cliente_required, get_user_profile

@cliente_required
def cliente_dashboard(request):
    """
    Dashboard específico para clientes
    """
    perfil = get_user_profile(request.user)

    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, 'No se encontró información del cliente.')
        return redirect('catering:index')

    eventos = EventoSolicitado.objects.filter(id_cliente=cliente).order_by('-fecha')

    total_eventos = eventos.count()
    eventos_activos = eventos.filter(estado__in=['SOLICITADO', 'CONFIRMADO', 'EN_PROCESO']).count()
    eventos_finalizados = eventos.filter(estado='FINALIZADO').count()
    gasto_total = sum(evento.precio_total for evento in eventos if evento.precio_total)

    eventos_confirmados = eventos.filter(
        estado__in=['CONFIRMADO', 'EN_PROCESO', 'FINALIZADO']
    ).order_by('-fecha')[:10]

    promedio_por_evento = 0
    if eventos_confirmados.exists():
        promedio_por_evento = gasto_total / eventos_confirmados.count()

    from django.utils import timezone
    from datetime import timedelta
    eventos_proximos = eventos.filter(
        fecha__gte=timezone.now().date(),
        fecha__lte=timezone.now().date() + timedelta(days=30)
    ).order_by('fecha', 'hora')[:5]
    
    context = {
        'cliente': cliente,
        'perfil': perfil,
        'total_eventos': total_eventos,
        'eventos_activos': eventos_activos,
        'eventos_finalizados': eventos_finalizados,
        'eventos_proximos': eventos_proximos,
        'eventos': eventos[:10],
        'eventos_confirmados': eventos_confirmados,
        'gasto_total': gasto_total,
        'promedio_por_evento': promedio_por_evento,
    }
    
    return render(request, 'catering/cliente_dashboard.html', context)

@cliente_required
def cliente_eventos(request):
    """
    Lista de eventos del cliente
    """
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, 'No se encontró información del cliente.')
        return redirect('catering:index')

    estado = request.GET.get('estado', '')
    tipo = request.GET.get('tipo', '')
    
    eventos = EventoSolicitado.objects.filter(id_cliente=cliente)
    
    if estado:
        eventos = eventos.filter(estado=estado)
    if tipo:
        eventos = eventos.filter(tipo_evento=tipo)
    
    eventos = eventos.order_by('-fecha')

    estados = EventoSolicitado.ESTADO_CHOICES
    tipos = EventoSolicitado.TIPO_EVENTO_CHOICES
    
    context = {
        'cliente': cliente,
        'eventos': eventos,
        'estados': estados,
        'tipos': tipos,
        'filtros': {
            'estado': estado,
            'tipo': tipo,
        }
    }
    
    return render(request, 'catering/cliente_eventos.html', context)

@cliente_required
def cliente_evento_detail(request, pk):
    """
    Detalle de un evento específico del cliente
    """
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, 'No se encontró información del cliente.')
        return redirect('catering:index')
    
    evento = get_object_or_404(EventoSolicitado, pk=pk, id_cliente=cliente)

    menu_items = evento.menuxproducto_set.all()

    servicios = evento.servicio_set.all()
    
    context = {
        'evento': evento,
        'cliente': cliente,
        'menu_items': menu_items,
        'servicios': servicios,
    }
    
    return render(request, 'catering/cliente_evento_detail.html', context)
