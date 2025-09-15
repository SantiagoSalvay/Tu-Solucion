from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import re

class Cliente(models.Model):
    """Modelo para gestionar los clientes de la empresa de catering"""
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    apellido = models.CharField(max_length=100, verbose_name="Apellido")
    tipo_doc = models.CharField(max_length=10, verbose_name="Tipo de Documento",
                            choices=[('DNI', 'DNI'), ('CUIL', 'CUIL'), ('PASAPORTE', 'PASAPORTE')])
    num_doc = models.CharField(max_length=20, verbose_name="Número de Documento", unique=True)
    email = models.EmailField(verbose_name="Email")
    domicilio = models.CharField(max_length=200, verbose_name="Domicilio")
    provincia = models.ForeignKey('Provincia', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Provincia")
    barrio = models.ForeignKey('Barrio', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Barrio")
    fecha_alta = models.DateField(auto_now_add=True, verbose_name="Fecha de Alta")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Usuario")
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['apellido', 'nombre']
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre}"
    
    def get_edad(self):
        """Calcula la edad del cliente basada en la fecha de nacimiento"""
        if self.fecha_nacimiento:
            return (timezone.now().date() - self.fecha_nacimiento).days // 365
        return None
    
    def tiene_vocal_segunda_letra(self):
        """Verifica si el nombre tiene una vocal como segunda letra"""
        if len(self.nombre) >= 2:
            return self.nombre[1].lower() in 'aeiouáéíóú'
        return False
    
    def crear_usuario(self, username=None, password=None):
        """Crea un usuario para el cliente"""
        if self.usuario:
            return self.usuario
        
        if not username:
            username = f"cliente_{self.num_doc}"
        
        if not password:
            password = f"cliente{self.num_doc}"

        user = User.objects.create_user(
            username=username,
            email=self.email,
            password=password,
            first_name=self.nombre,
            last_name=self.apellido,
            is_staff=False,
            is_superuser=False
        )

        PerfilUsuario.objects.create(
            usuario=user,
            tipo_usuario='CLIENTE',
            estado='ACTIVO',
            telefono='',
            fecha_nacimiento=self.fecha_nacimiento,
            direccion=self.domicilio
        )
        
        self.usuario = user
        self.save()
        
        return user

class Responsable(models.Model):
    """Modelo para gestionar los responsables de servicios"""
    id_responsable = models.AutoField(primary_key=True)
    nombre_apellido = models.CharField(max_length=200, verbose_name="Nombre y Apellido")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Email")
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name = "Responsable"
        verbose_name_plural = "Responsables"
        ordering = ['nombre_apellido']
    
    def __str__(self):
        return self.nombre_apellido

class TipoProducto(models.Model):
    """Modelo para los tipos de productos (bebidas, entradas, etc.)"""
    id_tipo_producto = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100, verbose_name="Descripción")
    
    class Meta:
        verbose_name = "Tipo de Producto"
        verbose_name_plural = "Tipos de Productos"
        ordering = ['descripcion']
    
    def __str__(self):
        return self.descripcion

class Producto(models.Model):
    """Modelo para los productos específicos de cada tipo"""
    id_producto = models.AutoField(primary_key=True)
    id_tipo_producto = models.ForeignKey(TipoProducto, on_delete=models.CASCADE, verbose_name="Tipo de Producto")
    descripcion = models.CharField(max_length=200, verbose_name="Descripción")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['id_tipo_producto', 'descripcion']
    
    def __str__(self):
        return f"{self.descripcion} - {self.id_tipo_producto}"

class Comprobante(models.Model):
    """Modelo para los comprobantes de pedido"""
    id_comprobante = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    fecha_pedido = models.DateField(auto_now_add=True, verbose_name="Fecha de Pedido")
    importe_total_productos = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Importe Total Productos")
    total_servicio = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Total del Servicio")
    precio_x_persona = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio por Persona")
    fecha_vigencia = models.DateField(verbose_name="Fecha de Vigencia")
    
    class Meta:
        verbose_name = "Comprobante"
        verbose_name_plural = "Comprobantes"
        ordering = ['-fecha_pedido']
    
    def __str__(self):
        return f"Comprobante {self.id_comprobante} - {self.id_cliente}"
    
    def save(self, *args, **kwargs):
        if not self.fecha_vigencia:
            self.fecha_vigencia = self.fecha_pedido + timedelta(days=10)
        super().save(*args, **kwargs)

class EventoSolicitado(models.Model):
    """Modelo para los eventos solicitados por los clientes"""
    TIPO_EVENTO_CHOICES = [
        ('CASAMIENTO', 'Casamiento'),
        ('CUMPLEAÑOS', 'Cumpleaños'),
        ('EVENTO_COMERCIAL', 'Evento Comercial'),
        ('OTRO', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('SOLICITADO', 'Solicitado'),
        ('CONFIRMADO', 'Confirmado'),
        ('EN_PROCESO', 'En Proceso'),
        ('FINALIZADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
        ('VENCIDO', 'Vencido'),
    ]
    
    id_evento = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    id_responsable = models.ForeignKey(Responsable, on_delete=models.CASCADE, verbose_name="Responsable")
    id_comprobante = models.ForeignKey(Comprobante, on_delete=models.CASCADE, verbose_name="Comprobante")
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES, verbose_name="Tipo de Evento")
    fecha = models.DateField(verbose_name="Fecha del Evento")
    hora = models.TimeField(verbose_name="Hora del Evento")
    ubicacion = models.CharField(max_length=300, verbose_name="Ubicación")
    cantidad_personas = models.PositiveIntegerField(verbose_name="Cantidad de Personas")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='SOLICITADO', verbose_name="Estado")
    precio_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Total", null=True, blank=True)
    precio_por_persona = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio por Persona", null=True, blank=True)

    tiene_sena = models.BooleanField(default=False, verbose_name="¿El cliente dejó seña?")
    monto_sena = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Monto de la Seña")
    fecha_sena = models.DateField(null=True, blank=True, verbose_name="Fecha de la Seña")
    observaciones_sena = models.TextField(max_length=500, blank=True, null=True, verbose_name="Observaciones sobre la Seña")
    
    class Meta:
        verbose_name = "Evento Solicitado"
        verbose_name_plural = "Eventos Solicitados"
        ordering = ['fecha', 'hora']
    
    def __str__(self):
        return f"Evento {self.id_evento} - {self.tipo_evento} - {self.fecha}"
    
    def verificar_disponibilidad(self):
        """Verifica si hay disponibilidad para la fecha y hora del evento"""
        eventos_mismo_dia = EventoSolicitado.objects.filter(
            fecha=self.fecha,
            estado__in=['SOLICITADO', 'CONFIRMADO', 'EN_PROCESO']
        ).exclude(id_evento=self.id_evento)
        
        return eventos_mismo_dia.count() < 10
    
    def get_porcentaje_sena(self):
        """Calcula el porcentaje de seña sobre el precio total"""
        if self.tiene_sena and self.monto_sena and self.precio_total:
            return (self.monto_sena / self.precio_total) * 100
        return 0
    
    def get_saldo_pendiente(self):
        """Calcula el saldo pendiente de pago"""
        if self.tiene_sena and self.monto_sena and self.precio_total:
            return self.precio_total - self.monto_sena
        return self.precio_total or 0
    
    def get_barrio(self):
        """Extrae el barrio de la ubicación"""

        if ',' in self.ubicacion:
            return self.ubicacion.split(',')[-1].strip()
        return self.ubicacion
    
    def calcular_precios(self):
        """Calcula los precios totales basados en el menú"""
        menu_items = MenuXTipoProducto.objects.filter(id_evento=self)
        total_productos = sum(item.precio_total for item in menu_items)
        
        if hasattr(self, 'id_comprobante'):
            self.id_comprobante.importe_total_productos = total_productos
            self.id_comprobante.total_servicio = total_productos * Decimal('1.3')
            self.id_comprobante.precio_x_persona = self.id_comprobante.total_servicio / self.cantidad_personas if self.cantidad_personas > 0 else 0
            self.id_comprobante.save()
            
            self.precio_total = self.id_comprobante.total_servicio
            self.precio_por_persona = self.id_comprobante.precio_x_persona
            self.save()

class MenuXTipoProducto(models.Model):
    """Modelo para los menús personalizados por tipo de producto"""
    id_menu = models.AutoField(primary_key=True)
    id_evento = models.ForeignKey(EventoSolicitado, on_delete=models.CASCADE, verbose_name="Evento")
    id_tipo_producto = models.ForeignKey(TipoProducto, on_delete=models.CASCADE, verbose_name="Tipo de Producto")
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name="Producto")
    cantidad_producto = models.PositiveIntegerField(verbose_name="Cantidad")
    precio_uni = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    precio_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Total")
    
    class Meta:
        verbose_name = "Menú por Tipo de Producto"
        verbose_name_plural = "Menús por Tipo de Producto"
        unique_together = ['id_evento', 'id_tipo_producto', 'id_producto']
    
    def __str__(self):
        return f"{self.id_evento} - {self.id_producto} - {self.cantidad_producto}"
    
    def save(self, *args, **kwargs):
        if not self.precio_uni:
            self.precio_uni = self.id_producto.precio
        self.precio_total = self.precio_uni * self.cantidad_producto
        super().save(*args, **kwargs)

class Senia(models.Model):
    """Modelo para gestionar las señas de los eventos"""
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADA', 'Pagada'),
        ('VENCIDA', 'Vencida'),
    ]
    
    id_senia = models.AutoField(primary_key=True)
    id_evento = models.OneToOneField(EventoSolicitado, on_delete=models.CASCADE, verbose_name="Evento")
    monto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Monto")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE', verbose_name="Estado")
    fecha_pago = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Pago")
    
    class Meta:
        verbose_name = "Seña"
        verbose_name_plural = "Señas"
    
    def __str__(self):
        return f"Seña {self.id_senia} - {self.id_evento} - {self.estado}"
    
    def calcular_monto(self):
        """Calcula el monto de la seña (30% del total del servicio)"""
        return self.id_evento.id_comprobante.total_servicio * Decimal('0.30')
    
    def save(self, *args, **kwargs):
        if not self.monto:
            self.monto = self.calcular_monto()
        super().save(*args, **kwargs)

class Personal(models.Model):
    """Modelo para gestionar el personal de la empresa"""
    TIPO_PERSONAL_CHOICES = [
        ('MOZO', 'Mozo'),
        ('COCINERO', 'Cocinero'),
        ('ASISTENTE', 'Asistente'),
        ('SUPERVISOR', 'Supervisor'),
    ]
    
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('VACACIONES', 'Vacaciones'),
        ('LICENCIA', 'Licencia'),
    ]
    
    id_personal = models.AutoField(primary_key=True)
    tipo_personal = models.CharField(max_length=20, choices=TIPO_PERSONAL_CHOICES, verbose_name="Tipo de Personal")
    nombre_y_apellido = models.CharField(max_length=200, verbose_name="Nombre y Apellido")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Email")
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Usuario")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO', verbose_name="Estado")
    
    class Meta:
        verbose_name = "Personal"
        verbose_name_plural = "Personal"
        ordering = ['tipo_personal', 'nombre_y_apellido']
    
    def __str__(self):
        return f"{self.nombre_y_apellido} - {self.tipo_personal}"

class Servicio(models.Model):
    """Modelo para gestionar los servicios de personal asignados a eventos"""
    id_servicio = models.AutoField(primary_key=True)
    id_evento = models.ForeignKey(EventoSolicitado, on_delete=models.CASCADE, verbose_name="Evento")
    id_personal = models.ForeignKey(Personal, on_delete=models.CASCADE, verbose_name="Personal")
    cantidad_personal = models.IntegerField(verbose_name="Cantidad de Personal", default=1)
    estado = models.CharField(max_length=20, verbose_name="Estado",
                          choices=[('ASIGNADO', 'Asignado'), ('EN_SERVICIO', 'En Servicio'), ('COMPLETADO', 'Completado'), ('CANCELADO', 'Cancelado')])
    fecha_asignacion = models.DateField(auto_now_add=True, verbose_name="Fecha de Asignación")
    
    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ['-fecha_asignacion']
    
    def __str__(self):
        return f"{self.id_personal} - {self.id_evento}"

class PerfilUsuario(models.Model):
    """Modelo para extender el usuario de Django con información adicional"""
    TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('EMPLEADO', 'Empleado'),
        ('RESPONSABLE', 'Responsable'),
        ('CLIENTE', 'Cliente'),
    ]
    
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'Suspendido'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario")
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='EMPLEADO', verbose_name="Tipo de Usuario")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO', verbose_name="Estado")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento")
    direccion = models.CharField(max_length=200, blank=True, null=True, verbose_name="Dirección")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_ultimo_acceso = models.DateTimeField(blank=True, null=True, verbose_name="Último Acceso")
    notas = models.TextField(blank=True, null=True, verbose_name="Notas")
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
        ordering = ['usuario__username']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_usuario_display()}"
    
    def get_edad(self):
        """Calcula la edad del usuario"""
        if self.fecha_nacimiento:
            return (timezone.now().date() - self.fecha_nacimiento).days // 365
        return None
    
    def es_admin(self):
        """Verifica si el usuario es administrador"""
        return self.tipo_usuario == 'ADMIN' or self.usuario.is_superuser
    
    def es_empleado(self):
        """Verifica si el usuario es empleado"""
        return self.tipo_usuario == 'EMPLEADO'
    
    def es_responsable(self):
        """Verifica si el usuario es responsable"""
        return self.tipo_usuario == 'RESPONSABLE'
    
    def esta_activo(self):
        """Verifica si el usuario está activo"""
        return self.estado == 'ACTIVO' and self.usuario.is_active

class Provincia(models.Model):
    """Modelo para gestionar las provincias de Córdoba"""
    id_provincia = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Provincia", unique=True)
    codigo = models.CharField(max_length=10, verbose_name="Código", unique=True)
    activa = models.BooleanField(default=True, verbose_name="Activa")
    
    class Meta:
        verbose_name = "Provincia"
        verbose_name_plural = "Provincias"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Barrio(models.Model):
    """Modelo para gestionar los barrios de cada provincia"""
    id_barrio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Barrio")
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, verbose_name="Provincia")
    codigo_postal = models.CharField(max_length=10, verbose_name="Código Postal", blank=True, null=True)
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Barrio"
        verbose_name_plural = "Barrios"
        ordering = ['provincia__nombre', 'nombre']
        unique_together = ['nombre', 'provincia']
    
    def __str__(self):
        return f"{self.nombre}, {self.provincia.nombre}"