from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import EventoSolicitado, Cliente, Responsable, PerfilUsuario, MenuXTipoProducto, Personal, Servicio
from .decorators import responsable_required, get_user_profile
from .forms import EventoForm, EventoResponsableForm, MenuForm, AsignarPersonalForm, CambiarEstadoEventoForm, TrabajadorEventoForm

@responsable_required
def responsable_dashboard(request):
    """
    Dashboard específico para responsables
    """
    perfil = get_user_profile(request.user)

    try:
        responsable = Responsable.objects.get(email=request.user.email)
    except Responsable.DoesNotExist:
        messages.error(request, 'No se encontró información del responsable.')
        return redirect('catering:index')

    eventos = EventoSolicitado.objects.filter(id_responsable=responsable).order_by('-fecha')

    total_eventos = eventos.count()
    eventos_activos = eventos.filter(estado__in=['SOLICITADO', 'CONFIRMADO', 'EN_PROCESO']).count()
    eventos_finalizados = eventos.filter(estado='FINALIZADO').count()
    eventos_cancelados = eventos.filter(estado='CANCELADO').count()

    eventos_proximos = eventos.filter(
        fecha__gte=timezone.now().date(),
        fecha__lte=timezone.now().date() + timedelta(days=30)
    ).order_by('fecha', 'hora')[:5]

    eventos_hoy = eventos.filter(fecha=timezone.now().date()).order_by('hora')

    eventos_por_estado = eventos.values('estado').annotate(
        count=Count('id_evento')
    ).order_by('estado')
    
    context = {
        'responsable': responsable,
        'perfil': perfil,
        'total_eventos': total_eventos,
        'eventos_activos': eventos_activos,
        'eventos_finalizados': eventos_finalizados,
        'eventos_cancelados': eventos_cancelados,
        'eventos_proximos': eventos_proximos,
        'eventos_hoy': eventos_hoy,
        'eventos_por_estado': eventos_por_estado,
        'eventos': eventos[:10],
    }
    
    return render(request, 'catering/responsable_dashboard.html', context)

@responsable_required
def responsable_eventos(request):
    """
    Lista de eventos del responsable
    """
    try:
        responsable = Responsable.objects.get(email=request.user.email)
    except Responsable.DoesNotExist:
        messages.error(request, 'No se encontró información del responsable.')
        return redirect('catering:index')

    estado = request.GET.get('estado', '')
    tipo = request.GET.get('tipo', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    
    eventos = EventoSolicitado.objects.filter(id_responsable=responsable)
    
    if estado:
        eventos = eventos.filter(estado=estado)
    if tipo:
        eventos = eventos.filter(tipo_evento=tipo)
    if fecha_desde:
        eventos = eventos.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        eventos = eventos.filter(fecha__lte=fecha_hasta)
    
    eventos = eventos.order_by('-fecha')

    estados = EventoSolicitado.ESTADO_CHOICES
    tipos = EventoSolicitado.TIPO_EVENTO_CHOICES
    
    context = {
        'responsable': responsable,
        'eventos': eventos,
        'estados': estados,
        'tipos': tipos,
        'filtros': {
            'estado': estado,
            'tipo': tipo,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        }
    }
    
    return render(request, 'catering/responsable_eventos.html', context)

@responsable_required
def responsable_evento_detail(request, pk):
    """
    Detalle de un evento específico del responsable
    """
    try:
        responsable = Responsable.objects.get(email=request.user.email)
    except Responsable.DoesNotExist:
        messages.error(request, 'No se encontró información del responsable.')
        return redirect('catering:index')
    
    evento = get_object_or_404(EventoSolicitado, pk=pk, id_responsable=responsable)

    menu_items = evento.menuxproducto_set.all()

    servicios = evento.servicio_set.all()
    
    context = {
        'evento': evento,
        'responsable': responsable,
        'menu_items': menu_items,
        'servicios': servicios,
    }
    
    return render(request, 'catering/responsable_evento_detail.html', context)

@responsable_required
def responsable_crear_evento(request):
    """
    Crear nuevo evento (solo responsables)
    """
    try:
        responsable = Responsable.objects.get(email=request.user.email)
    except Responsable.DoesNotExist:
        messages.error(request, 'No se encontró información del responsable.')
        return redirect('catering:index')
    
    trabajadores_asignados = []
    
    if request.method == 'POST':
        form = EventoForm(request.POST)
        trabajador_form = TrabajadorEventoForm(request.POST)
        
        if form.is_valid():
            evento = form.save(commit=False)

            evento.id_responsable = responsable
            evento.estado = 'SOLICITADO'
            evento.save()

            trabajadores_data = request.POST.getlist('trabajadores')
            cantidades_data = request.POST.getlist('cantidades')
            
            for i, trabajador_id in enumerate(trabajadores_data):
                if trabajador_id and i < len(cantidades_data) and cantidades_data[i]:
                    try:
                        personal = Personal.objects.get(id_personal=trabajador_id)
                        cantidad = int(cantidades_data[i])

                        Servicio.objects.create(
                            id_evento=evento,
                            id_personal=personal,
                            cantidad_personal=cantidad,
                            estado='ASIGNADO'
                        )
                    except (Personal.DoesNotExist, ValueError):
                        continue
            
            messages.success(request, f'Evento {evento.tipo_evento} creado exitosamente.')
            return redirect('catering:responsable_evento_detail', pk=evento.pk)
    else:
        form = EventoForm()
        trabajador_form = TrabajadorEventoForm()

        form.fields['id_responsable'].initial = responsable
    
    context = {
        'form': form,
        'trabajador_form': trabajador_form,
        'trabajadores_asignados': trabajadores_asignados,
        'responsable': responsable,
        'title': 'Crear Nuevo Evento',
    }
    
    return render(request, 'catering/responsable_crear_evento.html', context)

@responsable_required
def responsable_editar_evento(request, pk):
    """
    Editar evento existente - solo cantidad de personal
    """
    try:
        responsable = Responsable.objects.get(email=request.user.email)
    except Responsable.DoesNotExist:
        messages.error(request, 'No se encontró información del responsable.')
        return redirect('catering:index')
    
    evento = get_object_or_404(EventoSolicitado, pk=pk, id_responsable=responsable)
    
    if request.method == 'POST':
        form = EventoResponsableForm(request.POST, instance=evento)
        if form.is_valid():
            evento = form.save()
            messages.success(request, f'Cantidad de personal actualizada exitosamente.')
            return redirect('catering:responsable_evento_detail', pk=evento.pk)
    else:
        form = EventoResponsableForm(instance=evento)
    
    context = {
        'form': form,
        'evento': evento,
        'responsable': responsable,
        'title': 'Editar Cantidad de Personal',
    }
    
    return render(request, 'catering/responsable_editar_evento.html', context)

@responsable_required
def responsable_asignar_personal(request, evento_id):
    """
    Asignar personal a un evento
    """
    try:
        responsable = Responsable.objects.get(email=request.user.email)
    except Responsable.DoesNotExist:
        messages.error(request, 'No se encontró información del responsable.')
        return redirect('catering:index')
    
    evento = get_object_or_404(EventoSolicitado, id_evento=evento_id, id_responsable=responsable)
    
    if request.method == 'POST':
        form = AsignarPersonalForm(request.POST)
        if form.is_valid():
            servicio = form.save(commit=False)
            servicio.id_evento = evento
            servicio.save()
            
            messages.success(request, f'Personal {servicio.id_personal} asignado exitosamente.')
            return redirect('catering:responsable_evento_detail', pk=evento.pk)
    else:
        form = AsignarPersonalForm()

    personal_asignado = Servicio.objects.filter(id_evento=evento)
    
    context = {
        'form': form,
        'evento': evento,
        'responsable': responsable,
        'personal_asignado': personal_asignado,
        'title': 'Asignar Personal',
    }
    
    return render(request, 'catering/responsable_asignar_personal.html', context)

@responsable_required
def responsable_cambiar_estado_evento(request, evento_id):
    """
    Cambiar estado de un evento
    """
    try:
        responsable = Responsable.objects.get(email=request.user.email)
    except Responsable.DoesNotExist:
        messages.error(request, 'No se encontró información del responsable.')
        return redirect('catering:index')
    
    evento = get_object_or_404(EventoSolicitado, id_evento=evento_id, id_responsable=responsable)
    
    if request.method == 'POST':
        form = CambiarEstadoEventoForm(request.POST, instance=evento)
        if form.is_valid():
            evento = form.save()
            messages.success(request, f'Estado del evento cambiado a {evento.get_estado_display()}.')
            return redirect('catering:responsable_evento_detail', pk=evento.pk)
    else:
        form = CambiarEstadoEventoForm(instance=evento)
    
    context = {
        'form': form,
        'evento': evento,
        'responsable': responsable,
        'title': 'Cambiar Estado del Evento',
    }
    
    return render(request, 'catering/responsable_cambiar_estado_evento.html', context)

@responsable_required
def eliminar_personal_asignado(request, servicio_id):
    """
    Eliminar personal asignado a un evento
    """
    try:
        responsable = Responsable.objects.get(email=request.user.email)
    except Responsable.DoesNotExist:
        messages.error(request, 'No se encontró información del responsable.')
        return redirect('catering:index')
    
    servicio = get_object_or_404(Servicio, id_servicio=servicio_id, id_evento__id_responsable=responsable)
    evento = servicio.id_evento
    
    if request.method == 'POST':
        personal_nombre = servicio.id_personal
        servicio.delete()
        messages.success(request, f'Personal {personal_nombre} eliminado del evento.')
        return redirect('catering:responsable_asignar_personal', evento_id=evento.id_evento)
    
    context = {
        'servicio': servicio,
        'evento': evento,
        'responsable': responsable,
    }
    
    return render(request, 'catering/eliminar_personal_asignado.html', context)
