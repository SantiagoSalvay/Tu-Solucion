from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, Max, Q
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from decimal import Decimal
from .models import (
    Cliente, Responsable, TipoProducto, Producto, Comprobante,
    EventoSolicitado, MenuXTipoProducto, Senia, Personal, Servicio, PerfilUsuario,
    Provincia, Barrio
)
from .forms import ClienteForm, EventoForm, MenuForm, PersonalForm, AsignarPersonalForm, CambiarEstadoEventoForm, ProductoForm, TipoProductoForm, RegistroForm, GestionarSenaForm

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

    total_eventos = EventoSolicitado.objects.count()
    eventos_este_mes = EventoSolicitado.objects.filter(
        fecha__month=timezone.now().month,
        fecha__year=timezone.now().year
    ).count()

    eventos_por_estado_raw = EventoSolicitado.objects.values('estado').annotate(
        count=Count('id_evento')
    ).order_by('estado')

    eventos_por_estado = []
    for estado in eventos_por_estado_raw:
        porcentaje = (estado['count'] / total_eventos * 100) if total_eventos > 0 else 0
        estado['porcentaje'] = round(porcentaje, 1)
        eventos_por_estado.append(estado)

    eventos_proximos = EventoSolicitado.objects.filter(
        fecha__gte=timezone.now().date(),
        fecha__lte=timezone.now().date() + timedelta(days=7)
    ).order_by('fecha', 'hora')[:10]

    personal_disponible = Personal.objects.filter(estado='ACTIVO').count()

    total_clientes = Cliente.objects.count()
    
    context = {
        'total_eventos': total_eventos,
        'eventos_este_mes': eventos_este_mes,
        'eventos_por_estado': eventos_por_estado,
        'eventos_proximos': eventos_proximos,
        'personal_disponible': personal_disponible,
        'total_clientes': total_clientes,
    }
    return render(request, 'catering/dashboard.html', context)

@login_required
def cliente_list(request):
    """Lista de clientes"""
    clientes = Cliente.objects.all().order_by('apellido', 'nombre')

    search = request.GET.get('search')
    if search:
        clientes = clientes.filter(
            Q(nombre__icontains=search) |
            Q(apellido__icontains=search) |
            Q(email__icontains=search) |
            Q(num_doc__icontains=search)
        )

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

    total_eventos = eventos.count()
    eventos_completados = eventos.filter(estado='FINALIZADO').count()
    eventos_pendientes = eventos.filter(estado__in=['SOLICITADO', 'CONFIRMADO', 'EN_PROCESO']).count()

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

@login_required
def evento_list(request):
    """Lista de eventos"""
    eventos = EventoSolicitado.objects.select_related('id_cliente', 'id_responsable').all().order_by('-fecha')

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
    """Crear nuevo evento - Solo Admin y Responsables"""

    user_profile = getattr(request.user, 'perfilusuario', None)
    if not user_profile or user_profile.tipo_usuario not in ['ADMIN', 'RESPONSABLE']:
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para crear eventos. Solo administradores y responsables pueden crear eventos.')
            return redirect('catering:index')
    
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():

            evento = form.save(commit=False)

            from catering.models import Comprobante
            comprobante = Comprobante.objects.create(
                id_cliente=evento.id_cliente,
                fecha_pedido=timezone.now().date(),
                importe_total_productos=0.00,
                total_servicio=0.00,
                precio_x_persona=0.00,
                fecha_vigencia=evento.fecha
            )

            evento.id_comprobante = comprobante

            evento.save()
            
            messages.success(request, f'Evento {evento} creado exitosamente.')
            return redirect('catering:evento_detail', pk=evento.pk)
    else:
        form = EventoForm()
    
    context = {
        'form': form,
        'title': 'Nuevo Evento',
    }
    return render(request, 'catering/evento_form.html', context)

@login_required
def evento_update(request, pk):
    """Actualizar evento - Solo Admin y Responsables"""
    evento = get_object_or_404(EventoSolicitado, pk=pk)

    user_profile = getattr(request.user, 'perfilusuario', None)
    if not user_profile or user_profile.tipo_usuario not in ['ADMIN', 'RESPONSABLE']:
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para editar eventos.')
            return redirect('catering:evento_detail', pk=pk)

    if user_profile and user_profile.tipo_usuario == 'RESPONSABLE':
        if evento.id_responsable and evento.id_responsable.usuario != request.user:
            messages.error(request, 'No tienes permisos para editar este evento.')
            return redirect('catering:evento_detail', pk=pk)
    
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            evento = form.save()
            messages.success(request, f'Evento {evento} actualizado exitosamente.')
            return redirect('catering:evento_detail', pk=evento.pk)
    else:
        form = EventoForm(instance=evento)
    
    context = {
        'form': form,
        'evento': evento,
        'title': 'Editar Evento',
    }
    return render(request, 'catering/evento_form.html', context)

@login_required
def consulta_cumpleanos(request):
    """Consulta de marketing - Reporte de cumpleaños para recordatorios - Solo Admin"""

    user_profile = getattr(request.user, 'perfilusuario', None)
    if not user_profile or user_profile.tipo_usuario != 'ADMIN':
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para acceder a consultas de marketing.')
            return redirect('catering:index')
    
    from decimal import Decimal

    mes = request.GET.get('mes', timezone.now().month)
    incluir_vocal = request.GET.get('incluir_vocal', 'true') == 'true'
    
    try:
        mes = int(mes)
        if mes < 1 or mes > 12:
            mes = timezone.now().month
    except (ValueError, TypeError):
        mes = timezone.now().month

    clientes_cumpleanos = Cliente.objects.filter(
        fecha_nacimiento__month=mes
    ).exclude(
        fecha_nacimiento__isnull=True
    ).order_by('fecha_nacimiento__day', 'apellido', 'nombre')

    clientes_filtrados = []
    total_monto = Decimal('0')
    
    for cliente in clientes_cumpleanos:

        if incluir_vocal and not cliente.tiene_vocal_segunda_letra():
            continue

        edad = cliente.get_edad() if cliente.fecha_nacimiento else None

        eventos_cliente = EventoSolicitado.objects.filter(id_cliente=cliente)
        monto_total = Decimal('0')
        cantidad_eventos = eventos_cliente.count()
        
        for evento in eventos_cliente:
            if hasattr(evento, 'id_comprobante') and evento.id_comprobante:
                monto_total += evento.id_comprobante.total_servicio or Decimal('0')

        ultimo_evento = eventos_cliente.order_by('-fecha').first()
        
        clientes_filtrados.append({
            'cliente': cliente,
            'edad': edad,
            'monto_total': monto_total,
            'cantidad_eventos': cantidad_eventos,
            'ultimo_evento': ultimo_evento,
            'tiene_vocal_segunda_letra': cliente.tiene_vocal_segunda_letra()
        })
        
        total_monto += monto_total

    total_clientes = len(clientes_filtrados)
    promedio_monto = total_monto / total_clientes if total_clientes > 0 else Decimal('0')

    clientes_por_edad = {
        '18-30': 0,
        '31-50': 0,
        '51-70': 0,
        '70+': 0
    }
    
    for cliente_data in clientes_filtrados:
        edad = cliente_data['edad']
        if edad:
            if 18 <= edad <= 30:
                clientes_por_edad['18-30'] += 1
            elif 31 <= edad <= 50:
                clientes_por_edad['31-50'] += 1
            elif 51 <= edad <= 70:
                clientes_por_edad['51-70'] += 1
            else:
                clientes_por_edad['70+'] += 1

    meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    context = {
        'clientes': clientes_filtrados,
        'mes': mes,
        'mes_nombre': meses.get(mes, ''),
        'total_clientes': total_clientes,
        'total_monto': total_monto,
        'promedio_monto': promedio_monto,
        'clientes_por_edad': clientes_por_edad,
        'incluir_vocal': incluir_vocal,
        'filtros': {
            'mes': mes,
            'incluir_vocal': incluir_vocal,
        }
    }
    return render(request, 'catering/consulta_cumpleanos.html', context)

@login_required
def personal_list(request):
    """Lista de personal"""
    personal = Personal.objects.all().order_by('tipo_personal', 'nombre_y_apellido')

    tipo = request.GET.get('tipo')
    estado = request.GET.get('estado')
    
    if tipo:
        personal = personal.filter(tipo_personal=tipo)
    if estado:
        personal = personal.filter(estado=estado)

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
    """Crear nuevo miembro del personal - Solo Admin"""

    user_profile = getattr(request.user, 'perfilusuario', None)
    if not user_profile or user_profile.tipo_usuario != 'ADMIN':
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para crear personal. Solo administradores pueden gestionar personal.')
            return redirect('catering:index')
    
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

@login_required
def productos_list(request):
    """Lista todos los productos disponibles"""
    productos = Producto.objects.all().select_related('id_tipo_producto')

    tipo_filter = request.GET.get('tipo')
    disponible_filter = request.GET.get('disponible')
    
    if tipo_filter:
        productos = productos.filter(id_tipo_producto_id=tipo_filter)
    
    if disponible_filter is not None and disponible_filter != '':
        productos = productos.filter(disponible=disponible_filter == 'true')
    
    tipos_producto = TipoProducto.objects.all()
    
    context = {
        'productos': productos,
        'tipos_producto': tipos_producto,
        'filtros': {
            'tipo': tipo_filter,
            'disponible': disponible_filter,
        },
        'title': 'Lista de Productos'
    }
    return render(request, 'catering/productos_list.html', context)

@login_required
def producto_create(request):
    """Crear un nuevo producto - Solo Admin y Responsables"""

    user_profile = getattr(request.user, 'perfilusuario', None)
    if not user_profile or user_profile.tipo_usuario not in ['ADMIN', 'RESPONSABLE']:
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para crear productos.')
            return redirect('catering:index')
    
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

    eventos_usados = MenuXTipoProducto.objects.filter(
        id_producto=producto
    ).select_related('id_evento', 'id_evento__id_cliente')
    
    context = {
        'producto': producto,
        'eventos_usados': eventos_usados,
        'title': f'Producto - {producto.descripcion}'
    }
    return render(request, 'catering/producto_detail.html', context)

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

@login_required
def reserva_catering(request):
    """Vista para crear una nueva reserva de catering"""
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)

            if not evento.id_responsable:
                evento.id_responsable = Responsable.objects.first()

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
            try:

                producto_existente = MenuXTipoProducto.objects.filter(
                    id_evento=evento,
                    id_tipo_producto=form.cleaned_data['id_tipo_producto'],
                    id_producto=form.cleaned_data['id_producto']
                ).first()
                
                if producto_existente:

                    producto_existente.cantidad_producto += form.cleaned_data['cantidad_producto']
                    producto_existente.precio_total = producto_existente.precio_uni * producto_existente.cantidad_producto
                    producto_existente.save()
                    messages.success(request, 'Cantidad del producto actualizada exitosamente.')
                else:

                    menu_item = form.save(commit=False)
                    menu_item.id_evento = evento
                    menu_item.precio_uni = menu_item.id_producto.precio
                    menu_item.precio_total = menu_item.precio_uni * menu_item.cantidad_producto
                    menu_item.save()
                    messages.success(request, 'Producto agregado al menú exitosamente.')

                actualizar_comprobante(evento)
                return redirect('catering:editar_menu', evento_id=evento_id)
                
            except Exception as e:
                messages.error(request, f'Error al agregar producto al menú: {str(e)}')
                print(f"Error en editar_menu: {e}")
        else:

            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
            print(f"Errores del formulario: {form.errors}")
    else:
        form = MenuForm()

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

    actualizar_comprobante(menu_item.id_evento)
    
    messages.success(request, 'Producto eliminado del menú exitosamente.')
    return redirect('catering:editar_menu', evento_id=evento_id)

@login_required
def evento_delete(request, pk):
    """Eliminar un evento"""
    evento = get_object_or_404(EventoSolicitado, pk=pk)
    
    if request.method == 'POST':

        if Servicio.objects.filter(id_evento=evento).exists():
            messages.error(request, 'No se puede eliminar un evento que tiene personal asignado.')
            return redirect('catering:evento_detail', pk=pk)

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
    comprobante.total_servicio = total_productos * Decimal('1.3')
    comprobante.precio_x_persona = comprobante.total_servicio / evento.cantidad_personas if evento.cantidad_personas > 0 else 0
    comprobante.save()

    evento.precio_total = comprobante.total_servicio
    evento.precio_por_persona = comprobante.precio_x_persona
    evento.save()

def registro_usuario(request):
    """Vista para registro de nuevos usuarios (clientes)"""
    if request.user.is_authenticated:
        return redirect('catering:index')
    
    if request.method == 'POST':
        print(f"DEBUG - Datos POST recibidos: {request.POST}")
        form = RegistroForm(request.POST)
        print(f"DEBUG - Formulario válido: {form.is_valid()}")
        if not form.is_valid():
            print(f"DEBUG - Errores del formulario: {form.errors}")
        if form.is_valid():
            try:

                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    first_name=form.cleaned_data['nombre'],
                    last_name=form.cleaned_data['apellido']
                )

                PerfilUsuario.objects.create(
                    usuario=user,
                    tipo_usuario='CLIENTE'
                )

                cliente = Cliente.objects.create(
                    nombre=form.cleaned_data['nombre'],
                    apellido=form.cleaned_data['apellido'],
                    tipo_doc=form.cleaned_data['tipo_doc'],
                    num_doc=form.cleaned_data['num_doc'],
                    email=form.cleaned_data['email'],
                    domicilio=form.cleaned_data['domicilio'],
                    provincia=form.cleaned_data.get('provincia'),
                    barrio=None,
                    fecha_alta=timezone.now().date(),
                    usuario=user
                )
                
                messages.success(request, '¡Registro exitoso! Ya puedes iniciar sesión con tus credenciales.')
                return redirect('login')
                
            except Exception as e:
                messages.error(request, f'Error al crear el usuario: {str(e)}')
                print(f"Error en registro_usuario: {e}")
        else:

            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
            print(f"Errores del formulario: {form.errors}")
    else:
        form = RegistroForm()
    
    context = {
        'form': form,
        'title': 'Registro de Usuario'
    }
    return render(request, 'registration/registro.html', context)

def obtener_barrios_por_provincia(request):
    """Vista AJAX para obtener barrios de una provincia específica"""
    provincia_id = request.GET.get('provincia_id')
    
    if provincia_id:
        barrios = Barrio.objects.filter(provincia_id=provincia_id, activo=True).order_by('nombre')
        data = [{'id': barrio.id_barrio, 'nombre': barrio.nombre} for barrio in barrios]
    else:
        data = []
    
    return JsonResponse(data, safe=False)

@login_required
def gestionar_sena_evento(request, evento_id):
    """Vista para que los responsables gestionen la seña de un evento"""
    evento = get_object_or_404(EventoSolicitado, pk=evento_id)

    user_profile = getattr(request.user, 'perfilusuario', None)
    if not user_profile or (user_profile.tipo_usuario != 'RESPONSABLE' and not request.user.is_superuser):
        if user_profile and user_profile.tipo_usuario == 'RESPONSABLE':
            if evento.id_responsable.usuario != request.user:
                messages.error(request, 'No tienes permisos para gestionar este evento.')
                return redirect('catering:dashboard')
        else:
            messages.error(request, 'No tienes permisos para acceder a esta función.')
            return redirect('catering:dashboard')
    
    if request.method == 'POST':
        form = GestionarSenaForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Información de seña actualizada correctamente.')
            return redirect('catering:evento_detail', pk=evento.pk)
    else:
        form = GestionarSenaForm(instance=evento)
    
    context = {
        'form': form,
        'evento': evento,
        'title': f'Gestionar Seña - {evento.get_tipo_evento_display()}'
    }
    return render(request, 'catering/gestionar_sena.html', context)

@login_required
def empleado_dashboard(request):
    """Dashboard para empleados - muestra eventos donde deben trabajar"""
    user_profile = getattr(request.user, 'perfilusuario', None)

    if not user_profile or user_profile.tipo_usuario != 'EMPLEADO':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('catering:index')

    try:
        personal = Personal.objects.get(usuario=request.user)
    except Personal.DoesNotExist:
        messages.error(request, 'No se encontró información de personal para tu usuario.')
        return redirect('catering:index')

    servicios = Servicio.objects.filter(id_personal=personal)
    eventos_asignados = [servicio.id_evento for servicio in servicios]
    
    context = {
        'eventos_asignados': eventos_asignados,
        'personal': personal,
        'title': 'Dashboard Empleado'
    }
    return render(request, 'catering/empleado_dashboard.html', context)

@login_required
def responsable_dashboard(request):
    """Dashboard para responsables - muestra eventos asignados y herramientas de gestión"""
    user_profile = getattr(request.user, 'perfilusuario', None)

    if not user_profile or user_profile.tipo_usuario != 'RESPONSABLE':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('catering:index')

    try:
        responsable = Responsable.objects.get(usuario=request.user)
    except Responsable.DoesNotExist:
        messages.error(request, 'No se encontró información de responsable para tu usuario.')
        return redirect('catering:index')

    eventos_asignados = EventoSolicitado.objects.filter(id_responsable=responsable)
    eventos_confirmados = eventos_asignados.filter(estado__in=['CONFIRMADO', 'EN_PROCESO', 'FINALIZADO'])

    total_personal = Personal.objects.filter(estado='ACTIVO').count()
    ingresos_totales = eventos_confirmados.aggregate(
        total=Sum('precio_total')
    )['total'] or 0
    
    context = {
        'eventos_asignados': eventos_asignados,
        'eventos_confirmados': eventos_confirmados,
        'total_personal': total_personal,
        'ingresos_totales': ingresos_totales,
        'responsable': responsable,
        'title': 'Dashboard Responsable'
    }
    return render(request, 'catering/responsable_dashboard.html', context)
