from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import PerfilUsuario, Cliente, Personal, Responsable
from .decorators import admin_required, get_user_profile
from .forms import CrearUsuarioForm, CrearTrabajadorForm, CrearClienteForm, CrearResponsableForm

@admin_required
def admin_dashboard(request):
    """
    Dashboard específico para administradores
    """
    perfil = get_user_profile(request.user)

    from .models import EventoSolicitado
    from django.utils import timezone
    from django.db.models import Count
    
    total_usuarios = User.objects.count()
    total_clientes = Cliente.objects.count()
    total_personal = Personal.objects.count()
    total_eventos = EventoSolicitado.objects.count()

    usuarios_por_tipo = PerfilUsuario.objects.values('tipo_usuario').annotate(
        count=Count('id')
    ).order_by('tipo_usuario')

    eventos_por_estado = EventoSolicitado.objects.values('estado').annotate(
        count=Count('id_evento')
    ).order_by('estado')

    usuarios_recientes = User.objects.order_by('-date_joined')[:5]
    
    context = {
        'perfil': perfil,
        'total_usuarios': total_usuarios,
        'total_clientes': total_clientes,
        'total_personal': total_personal,
        'total_eventos': total_eventos,
        'usuarios_por_tipo': usuarios_por_tipo,
        'eventos_por_estado': eventos_por_estado,
        'usuarios_recientes': usuarios_recientes,
    }
    
    return render(request, 'catering/admin_dashboard.html', context)

@admin_required
def crear_usuario_admin(request):
    """
    Vista para crear usuarios con rol de administrador
    """
    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            with transaction.atomic():

                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    is_staff=form.cleaned_data['tipo_usuario'] == 'ADMIN',
                    is_superuser=form.cleaned_data['tipo_usuario'] == 'ADMIN'
                )

                PerfilUsuario.objects.create(
                    usuario=user,
                    tipo_usuario=form.cleaned_data['tipo_usuario'],
                    estado=form.cleaned_data['estado'],
                    telefono=form.cleaned_data.get('telefono', ''),
                    fecha_nacimiento=form.cleaned_data.get('fecha_nacimiento'),
                    direccion=form.cleaned_data.get('direccion', ''),
                    notas=form.cleaned_data.get('notas', '')
                )
                
                messages.success(request, f'Usuario {user.username} creado exitosamente.')
                return redirect('catering:admin_dashboard')
    else:
        form = CrearUsuarioForm()
    
    context = {
        'form': form,
        'title': 'Crear Usuario Administrativo',
    }
    
    return render(request, 'catering/crear_usuario_admin.html', context)

@admin_required
def crear_trabajador(request):
    """
    Vista para crear trabajadores
    """
    if request.method == 'POST':
        form = CrearTrabajadorForm(request.POST)
        if form.is_valid():
            with transaction.atomic():

                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['nombre_y_apellido'].split()[0] if form.cleaned_data['nombre_y_apellido'] else '',
                    last_name=' '.join(form.cleaned_data['nombre_y_apellido'].split()[1:]) if len(form.cleaned_data['nombre_y_apellido'].split()) > 1 else '',
                    is_staff=False,
                    is_superuser=False
                )

                PerfilUsuario.objects.create(
                    usuario=user,
                    tipo_usuario='EMPLEADO',
                    estado='ACTIVO',
                    telefono=form.cleaned_data['telefono'],
                    fecha_nacimiento=form.cleaned_data.get('fecha_nacimiento'),
                    direccion=form.cleaned_data.get('direccion', ''),
                    notas=f"Trabajador - {form.cleaned_data['tipo_personal']}"
                )

                Personal.objects.create(
                    tipo_personal=form.cleaned_data['tipo_personal'],
                    nombre_y_apellido=form.cleaned_data['nombre_y_apellido'],
                    telefono=form.cleaned_data['telefono'],
                    email=form.cleaned_data['email'],
                    estado=form.cleaned_data['estado']
                )
                
                messages.success(request, f'Trabajador {form.cleaned_data["nombre_y_apellido"]} creado exitosamente.')
                return redirect('catering:admin_dashboard')
    else:
        form = CrearTrabajadorForm()
    
    context = {
        'form': form,
        'title': 'Crear Trabajador',
    }
    
    return render(request, 'catering/crear_trabajador.html', context)

@admin_required
def crear_cliente(request):
    """
    Vista para crear clientes con cuenta de usuario
    """
    if request.method == 'POST':
        form = CrearClienteForm(request.POST)
        if form.is_valid():
            with transaction.atomic():

                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['nombre'],
                    last_name=form.cleaned_data['apellido'],
                    is_staff=False,
                    is_superuser=False
                )

                PerfilUsuario.objects.create(
                    usuario=user,
                    tipo_usuario='CLIENTE',
                    estado='ACTIVO',
                    telefono=form.cleaned_data.get('telefono', ''),
                    fecha_nacimiento=form.cleaned_data.get('fecha_nacimiento'),
                    direccion=form.cleaned_data['domicilio'],
                    notas='Cliente creado por administrador'
                )

                Cliente.objects.create(
                    nombre=form.cleaned_data['nombre'],
                    apellido=form.cleaned_data['apellido'],
                    tipo_doc=form.cleaned_data['tipo_doc'],
                    num_doc=form.cleaned_data['num_doc'],
                    email=form.cleaned_data['email'],
                    domicilio=form.cleaned_data['domicilio'],
                    fecha_nacimiento=form.cleaned_data.get('fecha_nacimiento'),
                    usuario=user
                )
                
                messages.success(request, f'Cliente {form.cleaned_data["nombre"]} {form.cleaned_data["apellido"]} creado exitosamente.')
                return redirect('catering:admin_dashboard')
    else:
        form = CrearClienteForm()
    
    context = {
        'form': form,
        'title': 'Crear Cliente',
    }
    
    return render(request, 'catering/crear_cliente.html', context)

@admin_required
def crear_responsable(request):
    """
    Vista para crear responsables con usuario y contraseña
    """
    if request.method == 'POST':
        form = CrearResponsableForm(request.POST)
        if form.is_valid():
            with transaction.atomic():

                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['nombre_apellido'].split()[0] if form.cleaned_data['nombre_apellido'] else '',
                    last_name=' '.join(form.cleaned_data['nombre_apellido'].split()[1:]) if len(form.cleaned_data['nombre_apellido'].split()) > 1 else '',
                    is_staff=False,
                    is_superuser=False
                )

                PerfilUsuario.objects.create(
                    usuario=user,
                    tipo_usuario='RESPONSABLE',
                    estado='ACTIVO',
                    telefono=form.cleaned_data['telefono'],
                    direccion=form.cleaned_data.get('direccion', ''),
                    notas='Responsable creado por administrador'
                )

                Responsable.objects.create(
                    nombre_apellido=form.cleaned_data['nombre_apellido'],
                    telefono=form.cleaned_data['telefono'],
                    email=form.cleaned_data['email'],
                    usuario=user
                )
                
                messages.success(request, f'Responsable {form.cleaned_data["nombre_apellido"]} creado exitosamente.')
                return redirect('catering:admin_dashboard')
    else:
        form = CrearResponsableForm()
    
    context = {
        'form': form,
        'title': 'Crear Responsable',
    }
    
    return render(request, 'catering/crear_responsable.html', context)

@admin_required
def gestion_usuarios(request):
    """
    Vista para gestionar todos los usuarios del sistema
    """
    usuarios = User.objects.all().order_by('-date_joined')

    tipo_usuario = request.GET.get('tipo_usuario', '')
    estado = request.GET.get('estado', '')
    
    if tipo_usuario:
        usuarios = usuarios.filter(perfilusuario__tipo_usuario=tipo_usuario)
    if estado:
        usuarios = usuarios.filter(perfilusuario__estado=estado)

    tipos_usuario = PerfilUsuario.TIPO_USUARIO_CHOICES
    estados = PerfilUsuario.ESTADO_CHOICES
    
    context = {
        'usuarios': usuarios,
        'tipos_usuario': tipos_usuario,
        'estados': estados,
        'filtros': {
            'tipo_usuario': tipo_usuario,
            'estado': estado,
        }
    }
    
    return render(request, 'catering/gestion_usuarios.html', context)
