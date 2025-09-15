from django.urls import path
from . import views, views_clientes, views_trabajadores, views_admin, views_responsables

app_name = 'catering'

urlpatterns = [
    # Vistas principales
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # URLs de Clientes
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/nuevo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/', views.cliente_detail, name='cliente_detail'),
    path('clientes/<int:pk>/editar/', views.cliente_update, name='cliente_update'),
    path('clientes/<int:pk>/eliminar/', views.cliente_delete, name='cliente_delete'),
    
    # URLs de Eventos
    path('eventos/', views.evento_list, name='evento_list'),
    path('eventos/nuevo/', views.evento_create, name='evento_create'),
    path('eventos/<int:pk>/', views.evento_detail, name='evento_detail'),
    path('eventos/<int:pk>/editar/', views.evento_update, name='evento_update'),
    path('eventos/<int:evento_id>/asignar-personal/', views.asignar_personal, name='asignar_personal'),
    path('eventos/<int:evento_id>/cambiar-estado/', views.cambiar_estado_evento, name='cambiar_estado_evento'),
    path('servicios/<int:servicio_id>/eliminar/', views.eliminar_personal_asignado, name='eliminar_personal_asignado'),
    
    # URLs de Personal
    path('personal/', views.personal_list, name='personal_list'),
    path('personal/nuevo/', views.personal_create, name='personal_create'),
    path('personal/<int:pk>/', views.personal_detail, name='personal_detail'),
    path('personal/<int:pk>/editar/', views.personal_update, name='personal_update'),
    path('personal/<int:pk>/eliminar/', views.personal_delete, name='personal_delete'),
    
    # URLs de Productos
    path('productos/', views.productos_list, name='productos_list'),
    path('productos/crear/', views.producto_create, name='producto_create'),
    path('productos/<int:pk>/', views.producto_detail, name='producto_detail'),
    path('productos/<int:pk>/editar/', views.producto_update, name='producto_update'),
    path('productos/<int:pk>/eliminar/', views.producto_delete, name='producto_delete'),
    
    # URLs de Tipos de Producto
    path('tipos-producto/', views.tipos_producto_list, name='tipos_producto_list'),
    path('tipos-producto/crear/', views.tipo_producto_create, name='tipo_producto_create'),
    path('tipos-producto/<int:pk>/editar/', views.tipo_producto_update, name='tipo_producto_update'),
    path('tipos-producto/<int:pk>/eliminar/', views.tipo_producto_delete, name='tipo_producto_delete'),
    
    # URLs para personal y eventos
    path('eventos/<int:evento_id>/asignar-personal/', views.asignar_personal, name='asignar_personal'),
    path('eventos/<int:evento_id>/cambiar-estado/', views.cambiar_estado_evento, name='cambiar_estado_evento'),
    path('servicios/<int:servicio_id>/eliminar/', views.eliminar_personal_asignado, name='eliminar_personal_asignado'),
    
    # URLs para consultas
    path('consultas/cumpleanos/', views.consulta_cumpleanos, name='consulta_cumpleanos'),
    
    # URLs para clientes
    path('cliente/eventos/', views.cliente_eventos, name='cliente_eventos'),
    path('cliente/eventos/<int:pk>/', views.cliente_evento_detail, name='cliente_evento_detail'),
    
    # URLs de API para AJAX
    path('api/verificar-disponibilidad/', views.verificar_disponibilidad, name='verificar_disponibilidad'),
    path('api/productos-por-tipo/', views.obtener_productos_por_tipo, name='obtener_productos_por_tipo'),
    
    # URLs para Reserva de Catering
    path('reserva/', views.reserva_catering, name='reserva_catering'),
    path('eventos/<int:evento_id>/editar-menu/', views.editar_menu, name='editar_menu'),
    path('menu/<int:menu_id>/eliminar/', views.eliminar_producto_menu, name='eliminar_producto_menu'),
    path('eventos/<int:pk>/eliminar/', views.evento_delete, name='evento_delete'),
    
    # URLs para Clientes (vistas específicas)
    path('cliente/dashboard/', views_clientes.cliente_dashboard, name='cliente_dashboard'),
    path('cliente/eventos/', views_clientes.cliente_eventos, name='cliente_eventos'),
    path('cliente/eventos/<int:pk>/', views_clientes.cliente_evento_detail, name='cliente_evento_detail'),
    
    # URLs para Trabajadores
    path('trabajador/servicios/', views_trabajadores.trabajador_servicios, name='trabajador_servicios'),
    path('trabajador/servicios/<int:pk>/', views_trabajadores.trabajador_servicio_detail, name='trabajador_servicio_detail'),
    
    # URLs para Administradores
    path('admin/dashboard/', views_admin.admin_dashboard, name='admin_dashboard'),
    path('admin/crear-usuario/', views_admin.crear_usuario_admin, name='crear_usuario_admin'),
    path('admin/crear-trabajador/', views_admin.crear_trabajador, name='crear_trabajador'),
    path('admin/crear-responsable/', views_admin.crear_responsable, name='crear_responsable'),
    path('admin/crear-cliente/', views_admin.crear_cliente, name='crear_cliente'),
    path('admin/gestion-usuarios/', views_admin.gestion_usuarios, name='gestion_usuarios'),
    
    # URLs para Responsables
    path('responsable/dashboard/', views_responsables.responsable_dashboard, name='responsable_dashboard'),
    path('responsable/eventos/', views_responsables.responsable_eventos, name='responsable_eventos'),
    path('responsable/eventos/<int:pk>/', views_responsables.responsable_evento_detail, name='responsable_evento_detail'),
    path('responsable/eventos/crear/', views_responsables.responsable_crear_evento, name='responsable_crear_evento'),
    
    # URL para registro de usuarios
    path('registro/', views.registro_usuario, name='registro_usuario'),
    path('responsable/eventos/<int:pk>/editar/', views_responsables.responsable_editar_evento, name='responsable_editar_evento'),
    path('responsable/eventos/<int:evento_id>/asignar-personal/', views_responsables.responsable_asignar_personal, name='responsable_asignar_personal'),
    path('responsable/eventos/<int:evento_id>/cambiar-estado/', views_responsables.responsable_cambiar_estado_evento, name='responsable_cambiar_estado_evento'),
    path('responsable/servicios/<int:servicio_id>/eliminar/', views_responsables.eliminar_personal_asignado, name='eliminar_personal_asignado'),
    
    # API para cargar barrios dinámicamente
    path('api/barrios-por-provincia/', views.obtener_barrios_por_provincia, name='obtener_barrios_por_provincia'),
    
    # Gestión de seña
    path('eventos/<int:evento_id>/gestionar-sena/', views.gestionar_sena_evento, name='gestionar_sena_evento'),
    
    # Dashboards específicos
    path('empleado/dashboard/', views.empleado_dashboard, name='empleado_dashboard'),
    path('responsable/dashboard/', views.responsable_dashboard, name='responsable_dashboard'),
]
