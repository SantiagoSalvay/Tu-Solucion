from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Cliente, Responsable, TipoProducto, Producto, Comprobante,
    EventoSolicitado, MenuXTipoProducto, Senia, Personal, Servicio, PerfilUsuario
)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['id_cliente', 'apellido', 'nombre', 'tipo_doc', 'num_doc', 'email', 'fecha_alta']
    list_filter = ['tipo_doc', 'fecha_alta']
    search_fields = ['nombre', 'apellido', 'email', 'num_doc']
    readonly_fields = ['id_cliente', 'fecha_alta']
    ordering = ['apellido', 'nombre']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellido', 'tipo_doc', 'num_doc')
        }),
        ('Contacto', {
            'fields': ('email', 'domicilio')
        }),
        ('Sistema', {
            'fields': ('id_cliente', 'fecha_alta'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Responsable)
class ResponsableAdmin(admin.ModelAdmin):
    list_display = ['id_responsable', 'nombre_apellido', 'telefono', 'email']
    search_fields = ['nombre_apellido', 'email']
    readonly_fields = ['id_responsable']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre_apellido', 'telefono', 'email')
        }),
        ('Sistema', {
            'fields': ('id_responsable', 'usuario'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TipoProducto)
class TipoProductoAdmin(admin.ModelAdmin):
    list_display = ['id_tipo_producto', 'descripcion']
    search_fields = ['descripcion']
    readonly_fields = ['id_tipo_producto']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['id_producto', 'descripcion', 'id_tipo_producto', 'precio', 'disponible']
    list_filter = ['id_tipo_producto', 'disponible']
    search_fields = ['descripcion']
    readonly_fields = ['id_producto']
    list_editable = ['disponible']
    
    fieldsets = (
        ('Información del Producto', {
            'fields': ('descripcion', 'id_tipo_producto', 'precio', 'disponible')
        }),
        ('Sistema', {
            'fields': ('id_producto',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ['id_comprobante', 'id_cliente', 'fecha_pedido', 'total_servicio', 'precio_x_persona', 'fecha_vigencia']
    list_filter = ['fecha_pedido', 'fecha_vigencia']
    search_fields = ['id_cliente__nombre', 'id_cliente__apellido']
    readonly_fields = ['id_comprobante', 'fecha_pedido']
    date_hierarchy = 'fecha_pedido'
    
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('id_cliente',)
        }),
        ('Detalles del Pedido', {
            'fields': ('importe_total_productos', 'total_servicio', 'precio_x_persona')
        }),
        ('Fechas', {
            'fields': ('fecha_pedido', 'fecha_vigencia')
        }),
        ('Sistema', {
            'fields': ('id_comprobante',),
            'classes': ('collapse',)
        }),
    )


@admin.register(EventoSolicitado)
class EventoSolicitadoAdmin(admin.ModelAdmin):
    list_display = ['id_evento', 'tipo_evento', 'id_cliente', 'fecha', 'hora', 'cantidad_personas', 'estado', 'disponibilidad']
    list_filter = ['tipo_evento', 'estado', 'fecha']
    search_fields = ['id_cliente__nombre', 'id_cliente__apellido', 'ubicacion']
    readonly_fields = ['id_evento']
    date_hierarchy = 'fecha'
    list_editable = ['estado']
    
    def disponibilidad(self, obj):
        if obj.verificar_disponibilidad():
            return format_html('<span style="color: green;">✓ Disponible</span>')
        else:
            return format_html('<span style="color: red;">✗ No Disponible</span>')
    disponibilidad.short_description = 'Disponibilidad'
    
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('id_cliente', 'id_responsable')
        }),
        ('Detalles del Evento', {
            'fields': ('tipo_evento', 'fecha', 'hora', 'ubicacion', 'cantidad_personas')
        }),
        ('Estado y Comprobante', {
            'fields': ('estado', 'id_comprobante')
        }),
        ('Sistema', {
            'fields': ('id_evento',),
            'classes': ('collapse',)
        }),
    )


@admin.register(MenuXTipoProducto)
class MenuXTipoProductoAdmin(admin.ModelAdmin):
    list_display = ['id_menu', 'id_evento', 'id_tipo_producto', 'id_producto', 'cantidad_producto', 'precio_uni', 'precio_total']
    list_filter = ['id_tipo_producto', 'id_evento__tipo_evento']
    search_fields = ['id_evento__id_cliente__nombre', 'id_producto__descripcion']
    readonly_fields = ['id_menu', 'precio_total']
    
    fieldsets = (
        ('Evento y Producto', {
            'fields': ('id_evento', 'id_tipo_producto', 'id_producto')
        }),
        ('Cantidad y Precios', {
            'fields': ('cantidad_producto', 'precio_uni', 'precio_total')
        }),
        ('Sistema', {
            'fields': ('id_menu',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Senia)
class SeniaAdmin(admin.ModelAdmin):
    list_display = ['id_senia', 'id_evento', 'monto', 'estado', 'fecha_pago']
    list_filter = ['estado', 'fecha_pago']
    search_fields = ['id_evento__id_cliente__nombre', 'id_evento__id_cliente__apellido']
    readonly_fields = ['id_senia', 'monto']
    list_editable = ['estado']
    
    fieldsets = (
        ('Evento', {
            'fields': ('id_evento',)
        }),
        ('Información de Pago', {
            'fields': ('monto', 'estado', 'fecha_pago')
        }),
        ('Sistema', {
            'fields': ('id_senia',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display = ['id_personal', 'nombre_y_apellido', 'tipo_personal', 'telefono', 'email', 'estado']
    list_filter = ['tipo_personal', 'estado']
    search_fields = ['nombre_y_apellido', 'email']
    readonly_fields = ['id_personal']
    list_editable = ['estado']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre_y_apellido', 'tipo_personal', 'telefono', 'email')
        }),
        ('Estado', {
            'fields': ('estado',)
        }),
        ('Sistema', {
            'fields': ('id_personal',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ['id_servicio', 'id_evento', 'id_personal', 'cantidad_personal', 'estado', 'fecha_asignacion']
    list_filter = ['estado', 'id_personal__tipo_personal', 'fecha_asignacion']
    search_fields = ['id_evento__id_cliente__nombre', 'id_personal__nombre_y_apellido']
    readonly_fields = ['id_servicio', 'fecha_asignacion']
    list_editable = ['estado']
    
    fieldsets = (
        ('Evento y Personal', {
            'fields': ('id_evento', 'id_personal', 'cantidad_personal')
        }),
        ('Estado', {
            'fields': ('estado', 'fecha_asignacion')
        }),
        ('Sistema', {
            'fields': ('id_servicio',),
            'classes': ('collapse',)
        }),
    )


# Configuración para extender el admin de User
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'
    fk_name = 'usuario'


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'get_tipo_usuario', 'get_estado', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined', 'perfilusuario__tipo_usuario', 'perfilusuario__estado']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['username']
    
    def get_tipo_usuario(self, obj):
        try:
            return obj.perfilusuario.get_tipo_usuario_display()
        except:
            return 'Sin perfil'
    get_tipo_usuario.short_description = 'Tipo de Usuario'
    
    def get_estado(self, obj):
        try:
            estado = obj.perfilusuario.get_estado_display()
            if obj.perfilusuario.estado == 'ACTIVO':
                return format_html('<span style="color: green;">{}</span>', estado)
            elif obj.perfilusuario.estado == 'INACTIVO':
                return format_html('<span style="color: red;">{}</span>', estado)
            else:
                return format_html('<span style="color: orange;">{}</span>', estado)
        except:
            return 'Sin perfil'
    get_estado.short_description = 'Estado'


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo_usuario', 'estado', 'telefono', 'fecha_creacion', 'fecha_ultimo_acceso', 'get_edad']
    list_filter = ['tipo_usuario', 'estado', 'fecha_creacion']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'usuario__email']
    readonly_fields = ['fecha_creacion', 'fecha_ultimo_acceso']
    list_editable = ['tipo_usuario', 'estado']
    ordering = ['usuario__username']
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('usuario', 'tipo_usuario', 'estado')
        }),
        ('Información Personal', {
            'fields': ('telefono', 'fecha_nacimiento', 'direccion')
        }),
        ('Sistema', {
            'fields': ('fecha_creacion', 'fecha_ultimo_acceso', 'notas'),
            'classes': ('collapse',)
        }),
    )
    
    def get_edad(self, obj):
        edad = obj.get_edad()
        if edad:
            return f"{edad} años"
        return "No especificada"
    get_edad.short_description = 'Edad'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')


# Reemplazar el admin de User con el personalizado
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Configuración del sitio de administración
admin.site.site_header = "Tu Solución - Administración"
admin.site.site_title = "Tu Solución"
admin.site.index_title = "Panel de Administración"
