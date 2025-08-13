from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Max, Q
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from .models import (
    Cliente, Responsable, TipoProducto, Producto, Comprobante,
    EventoSolicitado, MenuXTipoProducto, Senia, Personal, Servicio
)
from .forms import ClienteForm, EventoForm, MenuForm


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
    
    context = {
        'cliente': cliente,
        'eventos': eventos,
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
            return redirect('cliente_detail', pk=cliente.pk)
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
            return redirect('cliente_detail', pk=cliente.pk)
    else:
        form = ClienteForm(instance=cliente)
    
    context = {
        'form': form,
        'cliente': cliente,
        'title': 'Editar Cliente',
    }
    return render(request, 'catering/cliente_form.html', context)


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
    
    context = {
        'personal': personal,
        'tipos': Personal.TIPO_PERSONAL_CHOICES,
        'estados': Personal.ESTADO_CHOICES,
        'filtros': {
            'tipo': tipo,
            'estado': estado,
        }
    }
    return render(request, 'catering/personal_list.html', context)


@login_required
def asignar_personal(request, evento_id):
    """Asignar personal a un evento"""
    evento = get_object_or_404(EventoSolicitado, pk=evento_id)
    
    if request.method == 'POST':
        personal_ids = request.POST.getlist('personal')
        cantidad = request.POST.getlist('cantidad')
        
        # Eliminar asignaciones existentes
        Servicio.objects.filter(id_evento=evento).delete()
        
        # Crear nuevas asignaciones
        for i, personal_id in enumerate(personal_ids):
            if personal_id and cantidad[i]:
                personal = get_object_or_404(Personal, pk=personal_id)
                Servicio.objects.create(
                    id_evento=evento,
                    id_personal=personal,
                    cantidad_personal=int(cantidad[i])
                )
        
        # Actualizar estado del evento
        evento.estado = 'CONFIRMADO'
        evento.save()
        
        messages.success(request, 'Personal asignado exitosamente.')
        return redirect('evento_detail', pk=evento.pk)
    
    # Obtener personal disponible
    personal_disponible = Personal.objects.filter(estado='ACTIVO')
    servicios_actuales = Servicio.objects.filter(id_evento=evento)
    
    context = {
        'evento': evento,
        'personal_disponible': personal_disponible,
        'servicios_actuales': servicios_actuales,
    }
    return render(request, 'catering/asignar_personal.html', context)


# Vistas de Productos
@login_required
def productos_list(request):
    """Lista de productos"""
    productos = Producto.objects.select_related('id_tipo_producto').all().order_by('id_tipo_producto', 'descripcion')
    
    # Filtros
    tipo = request.GET.get('tipo')
    disponible = request.GET.get('disponible')
    
    if tipo:
        productos = productos.filter(id_tipo_producto_id=tipo)
    if disponible is not None:
        productos = productos.filter(disponible=disponible == 'true')
    
    tipos_producto = TipoProducto.objects.all()
    
    context = {
        'productos': productos,
        'tipos_producto': tipos_producto,
        'filtros': {
            'tipo': tipo,
            'disponible': disponible,
        }
    }
    return render(request, 'catering/productos_list.html', context)


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
        productos = Producto.objects.filter(
            id_tipo_producto_id=tipo_id,
            disponible=True
        ).values('id_producto', 'descripcion', 'precio')
        return JsonResponse({'productos': list(productos)})
    
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
            menu_item = form.save(commit=False)
            menu_item.id_evento = evento
            menu_item.precio_uni = menu_item.id_producto.precio
            menu_item.precio_total = menu_item.precio_uni * menu_item.cantidad_producto
            menu_item.save()
            
            # Actualizar comprobante
            actualizar_comprobante(evento)
            
            messages.success(request, 'Producto agregado al menú exitosamente.')
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
    comprobante.total_servicio = total_productos * 1.3  # 30% de ganancia
    comprobante.precio_x_persona = comprobante.total_servicio / evento.cantidad_personas if evento.cantidad_personas > 0 else 0
    comprobante.save()
    
    # Actualizar precio total del evento
    evento.precio_total = comprobante.total_servicio
    evento.precio_por_persona = comprobante.precio_x_persona
    evento.save()
