from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Max, Q
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from decimal import Decimal
from .models import (
    Cliente, Responsable, TipoProducto, Producto, Comprobante,
    EventoSolicitado, MenuXTipoProducto, Senia, Personal, Servicio
)
from .forms import ClienteForm, EventoForm, MenuForm, PersonalForm, AsignarPersonalForm, CambiarEstadoEventoForm, ProductoForm, TipoProductoForm


def index(request):
    """Vista principal del sistema"""
    context = {
        'total_clientes': Cliente.objects.count(),
        'total_eventos': EventoSolicitado.objects.count(),
        'eventos_hoy': EventoSolicitado.objects.filter(fecha=timezone.now().date()).count(),
        'eventos_pendientes': EventoSolicitado.objects.filter(estado='SOLICITADO').count(),
        'personal_activo': Personal.objects.filter(estado='ACTIVO').count(),
    }
    return render(request, 'catering/index.html', context)


@login_required
def dashboard(request):
    """Dashboard principal para usuarios autenticados"""
    # Estadísticas generales
    total_eventos = EventoSolicitado.objects.count()
    eventos_este_mes = EventoSolicitado.objects.filter(
        fecha__month=timezone.now().month,
        fecha__year=timezone.now().year
    ).count()
    
    # Eventos por estado
    eventos_por_estado = EventoSolicitado.objects.values('estado').annotate(
        count=Count('id_evento')
    ).order_by('estado')
    
    # Eventos próximos (próximos 7 días)
    eventos_proximos = EventoSolicitado.objects.filter(
        fecha__gte=timezone.now().date(),
        fecha__lte=timezone.now().date() + timedelta(days=7)
    ).order_by('fecha', 'hora')[:10]
    
    # Personal disponible
    personal_disponible = Personal.objects.filter(estado='ACTIVO').count()
    
    context = {
        'total_eventos': total_eventos,
        'eventos_este_mes': eventos_este_mes,
        'eventos_por_estado': eventos_por_estado,
        'eventos_proximos': eventos_proximos,
        'personal_disponible': personal_disponible,
    }
    return render(request, 'catering/dashboard.html', context)


# Vistas de Clientes
@login_required
def cliente_list(request):
    """Lista de clientes"""
    clientes = Cliente.objects.all().order_by('apellido', 'nombre')
    
    # Filtros
    search = request.GET.get('search')
    if search:
        clientes = clientes.filter(
            Q(nombre__icontains=search) |
            Q(apellido__icontains=search) |
            Q(email__icontains=search) |
            Q(num_doc__icontains=search)
        )
    
    # Paginación
    paginator = Paginator(clientes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    return render(request, 'catering/cliente_list.html', context)


@login_required
def cliente_detail(request, pk):
    """Detalle de un cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    eventos = EventoSolicitado.objects.filter(id_cliente=cliente).order_by('-fecha')
    
    # Estadísticas del cliente
    total_eventos = eventos.count()
    eventos_completados = eventos.filter(estado='FINALIZADO').count()
    eventos_pendientes = eventos.filter(estado__in=['SOLICITADO', 'CONFIRMADO', 'EN_PROCESO']).count()
    
    # Calcular total facturado (suma de todos los eventos finalizados)
    total_facturado = eventos.filter(estado='FINALIZADO').aggregate(
        total=Sum('id_comprobante__total_servicio')
    )['total'] or 0
    
    context = {
        'cliente': cliente,
        'eventos': eventos,
        'total_eventos': total_eventos,
        'eventos_completados': eventos_completados,
        'eventos_pendientes': eventos_pendientes,
        'total_facturado': total_facturado,
    }
    return render(request, 'catering/cliente_detail.html', context)


@login_required
def cliente_create(request):
    """Crear nuevo cliente"""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'Cliente {cliente} creado exitosamente.')
            return redirect('catering:cliente_detail', pk=cliente.pk)
    else:
        form = ClienteForm()
    
    context = {
        'form': form,
        'title': 'Nuevo Cliente',
    }
    return render(request, 'catering/cliente_form.html', context)


@login_required
def cliente_update(request, pk):
    """Actualizar cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'Cliente {cliente} actualizado exitosamente.')
            return redirect('catering:cliente_detail', pk=cliente.pk)
    else:
        form = ClienteForm(instance=cliente)
    
    context = {
        'form': form,
        'cliente': cliente,
        'title': 'Editar Cliente',
    }
    return render(request, 'catering/cliente_form.html', context)


@login_required
def cliente_delete(request, pk):
    """Eliminar cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        # Verificar que no tenga eventos asociados
        if EventoSolicitado.objects.filter(id_cliente=cliente).exists():
            messages.error(request, 'No se puede eliminar un cliente que tiene eventos asociados.')
            return redirect('catering:cliente_detail', pk=pk)
        
        cliente.delete()
        messages.success(request, 'Cliente eliminado exitosamente.')
        return redirect('catering:cliente_list')
    
    context = {
        'cliente': cliente,
    }
    return render(request, 'catering/cliente_confirm_delete.html', context)


@login_required
def cliente_eventos(request):
    """Vista para que los clientes vean sus eventos"""
    if not hasattr(request.user, 'cliente'):
        messages.error(request, 'Acceso denegado. Solo clientes pueden acceder a esta vista.')
        return redirect('catering:index')
    
    cliente = request.user.cliente
    eventos = EventoSolicitado.objects.filter(id_cliente=cliente).order_by('-fecha')
    
    context = {
        'eventos': eventos,
        'cliente': cliente,
        'title': 'Mis Eventos'
    }
    return render(request, 'catering/cliente_eventos.html', context)


@login_required
def cliente_evento_detail(request, pk):
    """Vista para que los clientes vean el detalle de su evento"""
    if not hasattr(request.user, 'cliente'):
        messages.error(request, 'Acceso denegado. Solo clientes pueden acceder a esta vista.')
        return redirect('catering:index')
    
    cliente = request.user.cliente
    evento = get_object_or_404(EventoSolicitado, pk=pk, id_cliente=cliente)
    menu_items = MenuXTipoProducto.objects.filter(id_evento=evento).select_related('id_producto', 'id_tipo_producto')
    servicios = Servicio.objects.filter(id_evento=evento).select_related('id_personal')
    
    try:
        senia = Senia.objects.get(id_evento=evento)
    except Senia.DoesNotExist:
        senia = None
    
    context = {
        'evento': evento,
        'menu_items': menu_items,
        'servicios': servicios,
        'senia': senia,
        'cliente': cliente,
        'title': f'Mi Evento - {evento.tipo_evento}'
    }
    return render(request, 'catering/cliente_evento_detail.html', context)


# Vistas de Eventos
@login_required
def evento_list(request):
    """Lista de eventos"""
    eventos = EventoSolicitado.objects.select_related('id_cliente', 'id_responsable').all().order_by('-fecha')
    
    # Filtros
    estado = request.GET.get('estado')
    tipo = request.GET.get('tipo')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if estado:
        eventos = eventos.filter(estado=estado)
    if tipo:
        eventos = eventos.filter(tipo_evento=tipo)
    if fecha_desde:
        eventos = eventos.filter(fecha__gte=fecha_desde)
    if fecha_hasta:
        eventos = eventos.filter(fecha__lte=fecha_hasta)
    
    # Paginación
    paginator = Paginator(eventos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'estados': EventoSolicitado.ESTADO_CHOICES,
        'tipos': EventoSolicitado.TIPO_EVENTO_CHOICES,
        'filtros': {
            'estado': estado,
            'tipo': tipo,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
        }
    }
    return render(request, 'catering/evento_list.html', context)


@login_required
def evento_detail(request, pk):
    """Detalle de un evento"""
    evento = get_object_or_404(EventoSolicitado, pk=pk)
    menu_items = MenuXTipoProducto.objects.filter(id_evento=evento).select_related('id_producto', 'id_tipo_producto')
    servicios = Servicio.objects.filter(id_evento=evento).select_related('id_personal')
    
    try:
        senia = Senia.objects.get(id_evento=evento)
    except Senia.DoesNotExist:
        senia = None
    
    context = {
        'evento': evento,
        'menu_items': menu_items,
        'servicios': servicios,
        'senia': senia,
    }
    return render(request, 'catering/evento_detail.html', context)


@login_required
def evento_create(request):
    """Crear nuevo evento"""
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save()
            messages.success(request, f'Evento {evento} creado exitosamente.')
            return redirect('evento_detail', pk=evento.pk)
    else:
        form = EventoForm()
    
    context = {
        'form': form,
        'title': 'Nuevo Evento',
    }
    return render(request, 'catering/evento_form.html', context)


@login_required
def evento_update(request, pk):
    """Actualizar evento"""
    evento = get_object_or_404(EventoSolicitado, pk=pk)
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            evento = form.save()
            messages.success(request, f'Evento {evento} actualizado exitosamente.')
            return redirect('evento_detail', pk=evento.pk)
    else:
        form = EventoForm(instance=evento)
    
    context = {
        'form': form,
        'evento': evento,
        'title': 'Editar Evento',
    }
    return render(request, 'catering/evento_form.html', context)


# Vistas de Consultas
@login_required
def consulta_financiera(request):
    """Consulta financiera - Costo total de productos por servicio"""
    # Filtros
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    # Consulta base
    consulta = MenuXTipoProducto.objects.select_related(
        'id_evento', 'id_evento__id_cliente', 'id_producto'
    ).filter(
        cantidad_producto__gte=200,
        cantidad_producto__lte=500
    )
    
    # Aplicar filtros de fecha
    if fecha_desde:
        consulta = consulta.filter(id_evento__fecha__gte=fecha_desde)
    if fecha_hasta:
        consulta = consulta.filter(id_evento__fecha__lte=fecha_hasta)
    else:
        # Por defecto, últimos 3 meses
        tres_meses_atras = timezone.now().date() - timedelta(days=90)
        consulta = consulta.filter(id_evento__fecha__gte=tres_meses_atras)
    
    # Agrupar por evento y calcular totales
    resultados = consulta.values(
        'id_evento__id_evento',
        'id_evento__tipo_evento',
        'id_evento__fecha',
        'id_evento__id_cliente__nombre',
        'id_evento__id_cliente__apellido'
    ).annotate(
        total_productos=Sum('cantidad_producto'),
        costo_total=Sum('precio_total')
    ).order_by('-costo_total')
    
    context = {
        'resultados': resultados,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
    }
    return render(request, 'catering/consulta_financiera.html', context)


@login_required
def consulta_barrios(request):
    """Consulta de marketing - Barrios más solicitados"""
    # Filtrar solo eventos finalizados en Buenos Aires
    eventos_finalizados = EventoSolicitado.objects.filter(
        estado='FINALIZADO'
    ).exclude(
        ubicacion__isnull=True
    ).exclude(
        ubicacion__exact=''
    )
    
    # Extraer barrios (implementación básica)
    barrios_data = {}
    for evento in eventos_finalizados:
        barrio = evento.get_barrio()
        if barrio and 'buenos aires' in barrio.lower():
            if barrio not in barrios_data:
                barrios_data[barrio] = {
                    'cantidad_servicios': 0,
                    'servicio_mayor_costo': None,
                    'costo_maximo': 0
                }
            
            barrios_data[barrio]['cantidad_servicios'] += 1
            
            # Calcular costo del servicio
            costo_servicio = MenuXTipoProducto.objects.filter(
                id_evento=evento
            ).aggregate(
                total=Sum('precio_total')
            )['total'] or 0
            
            if costo_servicio > barrios_data[barrio]['costo_maximo']:
                barrios_data[barrio]['costo_maximo'] = costo_servicio
                barrios_data[barrio]['servicio_mayor_costo'] = evento
    
    # Ordenar por cantidad de servicios y tomar top 10
    barrios_ordenados = sorted(
        barrios_data.items(),
        key=lambda x: x[1]['cantidad_servicios'],
        reverse=True
    )[:10]
    
    context = {
        'barrios': barrios_ordenados,
    }
    return render(request, 'catering/consulta_barrios.html', context)


@login_required
def consulta_cumpleanos(request):
    """Consulta de marketing - Clientes con cumpleaños en el mes actual"""
    mes_actual = timezone.now().month
    
    # Filtrar clientes con cumpleaños en el mes actual y nombre con vocal como segunda letra
    clientes_cumpleanos = Cliente.objects.filter(
        fecha_alta__month=mes_actual  # Usando fecha_alta como aproximación
    )
    
    # Filtrar por vocal en segunda letra del nombre
    clientes_filtrados = []
    for cliente in clientes_cumpleanos:
        if cliente.tiene_vocal_segunda_letra():
            # Calcular edad (aproximada)
            edad = (timezone.now().date() - cliente.fecha_alta).days // 365
            
            # Calcular monto total cobrado
            monto_total = Comprobante.objects.filter(
                id_cliente=cliente
            ).aggregate(
                total=Sum('total_servicio')
            )['total'] or 0
            
            clientes_filtrados.append({
                'cliente': cliente,
                'edad': edad,
                'monto_total': monto_total
            })
    
    # Ordenar por monto total
    clientes_filtrados.sort(key=lambda x: x['monto_total'], reverse=True)
    
    context = {
        'clientes': clientes_filtrados,
        'mes_actual': mes_actual,
    }
    return render(request, 'catering/consulta_cumpleanos.html', context)


# Vistas de Personal
@login_required
def personal_list(request):
    """Lista de personal"""
    personal = Personal.objects.all().order_by('tipo_personal', 'nombre_y_apellido')
    
    # Filtros
    tipo = request.GET.get('tipo')
    estado = request.GET.get('estado')
    
    if tipo:
        personal = personal.filter(tipo_personal=tipo)
    if estado:
        personal = personal.filter(estado=estado)
    
    # Estadísticas
    total_personal = Personal.objects.count()
    personal_activo = Personal.objects.filter(estado='ACTIVO').count()
    mozos = Personal.objects.filter(tipo_personal='MOZO').count()
    cocineros = Personal.objects.filter(tipo_personal='COCINERO').count()
    
    context = {
        'personal': personal,
        'tipos': Personal.TIPO_PERSONAL_CHOICES,
        'estados': Personal.ESTADO_CHOICES,
        'filtros': {
            'tipo': tipo,
            'estado': estado,
        },
        'estadisticas': {
            'total': total_personal,
            'activos': personal_activo,
            'mozos': mozos,
            'cocineros': cocineros,
        }
    }
    return render(request, 'catering/personal_list.html', context)


@login_required
def personal_detail(request, pk):
    """Detalle de un miembro del personal"""
    personal = get_object_or_404(Personal, pk=pk)
    servicios = Servicio.objects.filter(id_personal=personal).select_related('id_evento', 'id_evento__id_cliente').order_by('-fecha_asignacion')
    
    # Estadísticas del personal
    total_servicios = servicios.count()
    servicios_completados = servicios.filter(estado='COMPLETADO').count()
    servicios_pendientes = servicios.filter(estado__in=['ASIGNADO', 'EN_SERVICIO']).count()
    
    context = {
        'personal': personal,
        'servicios': servicios,
        'total_servicios': total_servicios,
        'servicios_completados': servicios_completados,
        'servicios_pendientes': servicios_pendientes,
    }
    return render(request, 'catering/personal_detail.html', context)


@login_required
def personal_create(request):
    """Crear nuevo miembro del personal"""
    if request.method == 'POST':
        form = PersonalForm(request.POST)
        if form.is_valid():
            personal = form.save()
            messages.success(request, f'Personal {personal} creado exitosamente.')
            return redirect('catering:personal_detail', pk=personal.pk)
    else:
        form = PersonalForm()
    
    context = {
        'form': form,
        'title': 'Nuevo Personal',
    }
    return render(request, 'catering/personal_form.html', context)


@login_required
def personal_update(request, pk):
    """Actualizar miembro del personal"""
    personal = get_object_or_404(Personal, pk=pk)
    if request.method == 'POST':
        form = PersonalForm(request.POST, instance=personal)
        if form.is_valid():
            personal = form.save()
            messages.success(request, f'Personal {personal} actualizado exitosamente.')
            return redirect('catering:personal_detail', pk=personal.pk)
    else:
        form = PersonalForm(instance=personal)
    
    context = {
        'form': form,
        'personal': personal,
        'title': 'Editar Personal',
    }
    return render(request, 'catering/personal_form.html', context)


@login_required
def personal_delete(request, pk):
    """Eliminar miembro del personal"""
    personal = get_object_or_404(Personal, pk=pk)
    
    if request.method == 'POST':
        # Verificar que no tenga servicios asociados
        if Servicio.objects.filter(id_personal=personal).exists():
            messages.error(request, 'No se puede eliminar un miembro del personal que tiene servicios asociados.')
            return redirect('catering:personal_detail', pk=pk)
        
        personal.delete()
        messages.success(request, 'Personal eliminado exitosamente.')
        return redirect('catering:personal_list')
    
    context = {
        'personal': personal,
    }
    return render(request, 'catering/personal_confirm_delete.html', context)


@login_required
def asignar_personal(request, evento_id):
    """Vista para asignar personal a un evento"""
    evento = get_object_or_404(EventoSolicitado, id_evento=evento_id)
    
    if request.method == 'POST':
        form = AsignarPersonalForm(request.POST)
        if form.is_valid():
            servicio = form.save(commit=False)
            servicio.id_evento = evento
            servicio.save()
            
            messages.success(request, f'Personal {servicio.id_personal.nombre_y_apellido} asignado exitosamente.')
            return redirect('catering:evento_detail', pk=evento_id)
    else:
        form = AsignarPersonalForm()
    
    # Obtener personal ya asignado
    personal_asignado = Servicio.objects.filter(id_evento=evento).select_related('id_personal')
    
    context = {
        'evento': evento,
        'form': form,
        'personal_asignado': personal_asignado,
        'title': f'Asignar Personal - Evento {evento.id_evento}'
    }
    return render(request, 'catering/asignar_personal.html', context)


@login_required
def cambiar_estado_evento(request, evento_id):
    """Vista para cambiar el estado de un evento"""
    evento = get_object_or_404(EventoSolicitado, id_evento=evento_id)
    
    if request.method == 'POST':
        form = CambiarEstadoEventoForm(request.POST, instance=evento)
        if form.is_valid():
            evento = form.save()
            messages.success(request, f'Estado del evento cambiado a: {evento.get_estado_display()}')
            return redirect('catering:evento_detail', pk=evento_id)
    else:
        form = CambiarEstadoEventoForm(instance=evento)
    
    context = {
        'evento': evento,
        'form': form,
        'title': f'Cambiar Estado - Evento {evento.id_evento}'
    }
    return render(request, 'catering/cambiar_estado_evento.html', context)


@login_required
def eliminar_personal_asignado(request, servicio_id):
    """Eliminar personal asignado a un evento"""
    servicio = get_object_or_404(Servicio, id_servicio=servicio_id)
    evento_id = servicio.id_evento.id_evento
    
    if request.method == 'POST':
        nombre_personal = servicio.id_personal.nombre_y_apellido
        servicio.delete()
        messages.success(request, f'Personal {nombre_personal} eliminado del evento exitosamente.')
        return redirect('catering:asignar_personal', evento_id=evento_id)
    
    context = {
        'servicio': servicio,
        'title': 'Eliminar Personal Asignado'
    }
    return render(request, 'catering/eliminar_personal_asignado.html', context)


# Vistas de Productos
@login_required
def productos_list(request):
    """Lista todos los productos disponibles"""
    productos = Producto.objects.all().select_related('id_tipo_producto')
    
    # Filtros
    tipo_filter = request.GET.get('tipo')
    disponible_filter = request.GET.get('disponible')
    
    if tipo_filter:
        productos = productos.filter(id_tipo_producto_id=tipo_filter)
    
    if disponible_filter is not None:
        productos = productos.filter(disponible=disponible_filter == 'true')
    
    tipos_producto = TipoProducto.objects.all()
    
    context = {
        'productos': productos,
        'tipos_producto': tipos_producto,
        'title': 'Lista de Productos'
    }
    return render(request, 'catering/productos_list.html', context)


@login_required
def producto_create(request):
    """Crear un nuevo producto"""
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.descripcion}" creado exitosamente.')
            return redirect('catering:productos_list')
    else:
        form = ProductoForm()
    
    context = {
        'form': form,
        'title': 'Crear Nuevo Producto'
    }
    return render(request, 'catering/producto_form.html', context)


@login_required
def producto_update(request, pk):
    """Editar un producto existente"""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'Producto "{producto.descripcion}" actualizado exitosamente.')
            return redirect('catering:productos_list')
    else:
        form = ProductoForm(instance=producto)
    
    context = {
        'form': form,
        'producto': producto,
        'title': f'Editar Producto - {producto.descripcion}'
    }
    return render(request, 'catering/producto_form.html', context)


@login_required
def producto_delete(request, pk):
    """Eliminar un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        nombre_producto = producto.descripcion
        producto.delete()
        messages.success(request, f'Producto "{nombre_producto}" eliminado exitosamente.')
        return redirect('catering:productos_list')
    
    context = {
        'producto': producto,
        'title': f'Eliminar Producto - {producto.descripcion}'
    }
    return render(request, 'catering/producto_confirm_delete.html', context)


@login_required
def producto_detail(request, pk):
    """Ver detalles de un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    
    # Obtener eventos donde se usó este producto
    eventos_usados = MenuXTipoProducto.objects.filter(
        id_producto=producto
    ).select_related('id_evento', 'id_evento__id_cliente')
    
    context = {
        'producto': producto,
        'eventos_usados': eventos_usados,
        'title': f'Producto - {producto.descripcion}'
    }
    return render(request, 'catering/producto_detail.html', context)


# Vistas de Tipos de Producto
@login_required
def tipos_producto_list(request):
    """Lista todos los tipos de productos"""
    tipos = TipoProducto.objects.all()
    
    context = {
        'tipos': tipos,
        'title': 'Tipos de Productos'
    }
    return render(request, 'catering/tipos_producto_list.html', context)


@login_required
def tipo_producto_create(request):
    """Crear un nuevo tipo de producto"""
    if request.method == 'POST':
        form = TipoProductoForm(request.POST)
        if form.is_valid():
            tipo = form.save()
            messages.success(request, f'Tipo de producto "{tipo.descripcion}" creado exitosamente.')
            return redirect('catering:tipos_producto_list')
    else:
        form = TipoProductoForm()
    
    context = {
        'form': form,
        'title': 'Crear Nuevo Tipo de Producto'
    }
    return render(request, 'catering/tipo_producto_form.html', context)


@login_required
def tipo_producto_update(request, pk):
    """Editar un tipo de producto existente"""
    tipo = get_object_or_404(TipoProducto, pk=pk)
    
    if request.method == 'POST':
        form = TipoProductoForm(request.POST, instance=tipo)
        if form.is_valid():
            tipo = form.save()
            messages.success(request, f'Tipo de producto "{tipo.descripcion}" actualizado exitosamente.')
            return redirect('catering:tipos_producto_list')
    else:
        form = TipoProductoForm(instance=tipo)
    
    context = {
        'form': form,
        'tipo': tipo,
        'title': f'Editar Tipo de Producto - {tipo.descripcion}'
    }
    return render(request, 'catering/tipo_producto_form.html', context)


@login_required
def tipo_producto_delete(request, pk):
    """Eliminar un tipo de producto"""
    tipo = get_object_or_404(TipoProducto, pk=pk)
    
    # Verificar si hay productos asociados
    productos_asociados = Producto.objects.filter(id_tipo_producto=tipo)
    
    if request.method == 'POST':
        nombre_tipo = tipo.descripcion
        tipo.delete()
        messages.success(request, f'Tipo de producto "{nombre_tipo}" eliminado exitosamente.')
        return redirect('catering:tipos_producto_list')
    
    context = {
        'tipo': tipo,
        'productos_asociados': productos_asociados,
        'title': f'Eliminar Tipo de Producto - {tipo.descripcion}'
    }
    return render(request, 'catering/tipo_producto_confirm_delete.html', context)


# API Views para AJAX
def verificar_disponibilidad(request):
    """Verificar disponibilidad para una fecha específica"""
    fecha = request.GET.get('fecha')
    if fecha:
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            eventos_count = EventoSolicitado.objects.filter(
                fecha=fecha_obj,
                estado__in=['SOLICITADO', 'CONFIRMADO', 'EN_PROCESO']
            ).count()
            
            disponible = eventos_count < 10
            return JsonResponse({
                'disponible': disponible,
                'eventos_count': eventos_count,
                'max_eventos': 10
            })
        except ValueError:
            return JsonResponse({'error': 'Fecha inválida'}, status=400)
    
    return JsonResponse({'error': 'Fecha requerida'}, status=400)


def obtener_productos_por_tipo(request):
    """Obtener productos por tipo para el armado de menús"""
    tipo_id = request.GET.get('tipo_id')
    if tipo_id:
        try:
            productos = Producto.objects.filter(
                id_tipo_producto_id=tipo_id,
                disponible=True
            ).values('id_producto', 'descripcion', 'precio').order_by('descripcion')
            return JsonResponse({'productos': list(productos)})
        except Exception as e:
            return JsonResponse({'error': f'Error al obtener productos: {str(e)}'}, status=400)
    
    return JsonResponse({'error': 'Tipo de producto requerido'}, status=400)


# Vistas para Reserva de Catering
@login_required
def reserva_catering(request):
    """Vista para crear una nueva reserva de catering"""
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            
            # Asignar responsable por defecto si no hay uno seleccionado
            if not evento.id_responsable:
                evento.id_responsable = Responsable.objects.first()
            
            # Crear comprobante temporal
            comprobante = Comprobante.objects.create(
                id_cliente=evento.id_cliente,
                importe_total_productos=0,
                total_servicio=0,
                precio_x_persona=0,
                fecha_vigencia=timezone.now().date() + timedelta(days=10)
            )
            evento.id_comprobante = comprobante
            evento.save()
            
            messages.success(request, 'Reserva creada exitosamente. Ahora puedes agregar productos al menú.')
            return redirect('catering:editar_menu', evento_id=evento.id_evento)
    else:
        form = EventoForm()
    
    context = {
        'form': form,
        'title': 'Nueva Reserva de Catering'
    }
    return render(request, 'catering/reserva_catering.html', context)


@login_required
def editar_menu(request, evento_id):
    """Vista para editar el menú de un evento"""
    evento = get_object_or_404(EventoSolicitado, id_evento=evento_id)
    
    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            # Verificar si ya existe un producto del mismo tipo para este evento
            producto_existente = MenuXTipoProducto.objects.filter(
                id_evento=evento,
                id_tipo_producto=form.cleaned_data['id_tipo_producto'],
                id_producto=form.cleaned_data['id_producto']
            ).first()
            
            if producto_existente:
                # Si existe, actualizar la cantidad
                producto_existente.cantidad_producto += form.cleaned_data['cantidad_producto']
                producto_existente.precio_total = producto_existente.precio_uni * producto_existente.cantidad_producto
                producto_existente.save()
                messages.success(request, 'Cantidad del producto actualizada exitosamente.')
            else:
                # Si no existe, crear uno nuevo
                menu_item = form.save(commit=False)
                menu_item.id_evento = evento
                menu_item.precio_uni = menu_item.id_producto.precio
                menu_item.precio_total = menu_item.precio_uni * menu_item.cantidad_producto
                menu_item.save()
                messages.success(request, 'Producto agregado al menú exitosamente.')
            
            # Actualizar comprobante
            actualizar_comprobante(evento)
            return redirect('catering:editar_menu', evento_id=evento_id)
    else:
        form = MenuForm()
    
    # Obtener productos del menú actual
    menu_actual = MenuXTipoProducto.objects.filter(id_evento=evento).select_related('id_producto', 'id_tipo_producto')
    
    context = {
        'evento': evento,
        'form': form,
        'menu_actual': menu_actual,
        'title': f'Editar Menú - Evento {evento.id_evento}'
    }
    return render(request, 'catering/editar_menu.html', context)


@login_required
def eliminar_producto_menu(request, menu_id):
    """Eliminar un producto del menú"""
    menu_item = get_object_or_404(MenuXTipoProducto, id_menu=menu_id)
    evento_id = menu_item.id_evento.id_evento
    
    menu_item.delete()
    
    # Actualizar comprobante
    actualizar_comprobante(menu_item.id_evento)
    
    messages.success(request, 'Producto eliminado del menú exitosamente.')
    return redirect('catering:editar_menu', evento_id=evento_id)


@login_required
def evento_delete(request, pk):
    """Eliminar un evento"""
    evento = get_object_or_404(EventoSolicitado, pk=pk)
    
    if request.method == 'POST':
        # Verificar que no tenga personal asignado
        if Servicio.objects.filter(id_evento=evento).exists():
            messages.error(request, 'No se puede eliminar un evento que tiene personal asignado.')
            return redirect('catering:evento_detail', pk=pk)
        
        # Eliminar menú y comprobante asociados
        MenuXTipoProducto.objects.filter(id_evento=evento).delete()
        if hasattr(evento, 'id_comprobante'):
            evento.id_comprobante.delete()
        
        evento.delete()
        messages.success(request, 'Evento eliminado exitosamente.')
        return redirect('catering:evento_list')
    
    context = {
        'evento': evento,
    }
    return render(request, 'catering/evento_confirm_delete.html', context)


def actualizar_comprobante(evento):
    """Función auxiliar para actualizar el comprobante de un evento"""
    menu_items = MenuXTipoProducto.objects.filter(id_evento=evento)
    total_productos = sum(item.precio_total for item in menu_items)
    
    comprobante = evento.id_comprobante
    comprobante.importe_total_productos = total_productos
    comprobante.total_servicio = total_productos * Decimal('1.3')  # 30% de ganancia
    comprobante.precio_x_persona = comprobante.total_servicio / evento.cantidad_personas if evento.cantidad_personas > 0 else 0
    comprobante.save()
    
    # Actualizar precio total del evento
    evento.precio_total = comprobante.total_servicio
    evento.precio_por_persona = comprobante.precio_x_persona
    evento.save()
