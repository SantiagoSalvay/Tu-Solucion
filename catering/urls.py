from django.urls import path
from . import views

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
    
    # URLs para personal y eventos
    path('eventos/<int:evento_id>/asignar-personal/', views.asignar_personal, name='asignar_personal'),
    path('eventos/<int:evento_id>/cambiar-estado/', views.cambiar_estado_evento, name='cambiar_estado_evento'),
    path('servicios/<int:servicio_id>/eliminar/', views.eliminar_personal_asignado, name='eliminar_personal_asignado'),
    
    # URLs para consultas
    path('consultas/financiera/', views.consulta_financiera, name='consulta_financiera'),
    path('consultas/barrios/', views.consulta_barrios, name='consulta_barrios'),
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
]
