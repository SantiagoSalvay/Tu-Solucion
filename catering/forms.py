from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Cliente, Responsable, TipoProducto, Producto, Comprobante,
    EventoSolicitado, MenuXTipoProducto, Senia, Personal, Servicio
)


class ClienteForm(forms.ModelForm):
    """Formulario para crear y editar clientes"""
    
    # Campos para crear usuario
    crear_usuario = forms.BooleanField(
        required=False, 
        initial=True,
        label="Crear usuario para este cliente",
        help_text="Marcar para crear automáticamente un usuario con rol CLIENTE"
    )
    username_personalizado = forms.CharField(
        max_length=150,
        required=False,
        label="Nombre de usuario personalizado",
        help_text="Dejar vacío para generar automáticamente",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dejar vacío para generar automáticamente'})
    )
    password_personalizada = forms.CharField(
        max_length=128,
        required=False,
        label="Contraseña personalizada",
        help_text="Dejar vacío para generar automáticamente",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Dejar vacío para generar automáticamente'})
    )
    
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'tipo_doc', 'num_doc', 'email', 'domicilio', 'fecha_nacimiento']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el apellido'}),
            'tipo_doc': forms.Select(attrs={'class': 'form-select'}),
            'num_doc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el número de documento'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@email.com'}),
            'domicilio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el domicilio completo'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def clean_num_doc(self):
        """Validar que el número de documento sea único"""
        num_doc = self.cleaned_data['num_doc']
        if Cliente.objects.filter(num_doc=num_doc).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError('Ya existe un cliente con este número de documento.')
        return num_doc
    
    def clean_email(self):
        """Validar formato de email"""
        email = self.cleaned_data['email']
        if Cliente.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise ValidationError('Ya existe un cliente con este email.')
        return email
    
    def clean_username_personalizado(self):
        """Validar que el username sea único si se proporciona"""
        username = self.cleaned_data['username_personalizado']
        if username:
            from django.contrib.auth.models import User
            if User.objects.filter(username=username).exists():
                raise ValidationError('Ya existe un usuario con este nombre de usuario.')
        return username
    
    def save(self, commit=True):
        cliente = super().save(commit=False)
        
        if commit:
            cliente.save()
            
            # Crear usuario si se solicita
            if self.cleaned_data.get('crear_usuario') and not cliente.usuario:
                username = self.cleaned_data.get('username_personalizado')
                password = self.cleaned_data.get('password_personalizada')
                
                if not username:
                    username = f"cliente_{cliente.num_doc}"
                
                if not password:
                    password = f"cliente{cliente.num_doc}"
                
                try:
                    cliente.crear_usuario(username=username, password=password)
                except Exception as e:
                    # Si hay error al crear usuario, no fallar la creación del cliente
                    pass
        
        return cliente


class ResponsableForm(forms.ModelForm):
    """Formulario para crear y editar responsables"""
    
    class Meta:
        model = Responsable
        fields = ['nombre_apellido', 'telefono', 'email']
        widgets = {
            'nombre_apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre y apellido completo'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@email.com'}),
        }


class ProductoForm(forms.ModelForm):
    """Formulario para crear y editar productos"""
    
    class Meta:
        model = Producto
        fields = ['descripcion', 'id_tipo_producto', 'precio', 'disponible']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción del producto'}),
            'id_tipo_producto': forms.Select(attrs={'class': 'form-select'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EventoForm(forms.ModelForm):
    """Formulario para crear y editar eventos"""
    
    class Meta:
        model = EventoSolicitado
        fields = ['id_cliente', 'id_responsable', 'tipo_evento', 'fecha', 'hora', 'ubicacion', 'cantidad_personas']
        widgets = {
            'id_cliente': forms.Select(attrs={'class': 'form-select'}),
            'id_responsable': forms.Select(attrs={'class': 'form-select'}),
            'tipo_evento': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección completa del evento'}),
            'cantidad_personas': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
    
    def clean_fecha(self):
        """Validar que la fecha no sea anterior a hoy"""
        fecha = self.cleaned_data['fecha']
        if fecha < timezone.now().date():
            raise ValidationError('La fecha del evento no puede ser anterior a hoy.')
        return fecha
    
    def clean_cantidad_personas(self):
        """Validar cantidad de personas"""
        cantidad = self.cleaned_data['cantidad_personas']
        if cantidad <= 0:
            raise ValidationError('La cantidad de personas debe ser mayor a 0.')
        if cantidad > 1000:
            raise ValidationError('La cantidad de personas no puede ser mayor a 1000.')
        return cantidad


class MenuForm(forms.ModelForm):
    """Formulario para crear menús personalizados"""
    
    class Meta:
        model = MenuXTipoProducto
        fields = ['id_tipo_producto', 'id_producto', 'cantidad_producto']
        widgets = {
            'id_tipo_producto': forms.Select(attrs={'class': 'form-select', 'id': 'tipo-producto'}),
            'id_producto': forms.Select(attrs={'class': 'form-select', 'id': 'producto'}),
            'cantidad_producto': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo productos disponibles
        self.fields['id_producto'].queryset = Producto.objects.filter(disponible=True)


class ComprobanteForm(forms.ModelForm):
    """Formulario para crear comprobantes"""
    
    class Meta:
        model = Comprobante
        fields = ['id_cliente', 'importe_total_productos', 'total_servicio', 'precio_x_persona', 'fecha_vigencia']
        widgets = {
            'id_cliente': forms.Select(attrs={'class': 'form-select'}),
            'importe_total_productos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'total_servicio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'precio_x_persona': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'fecha_vigencia': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def clean_fecha_vigencia(self):
        """Validar fecha de vigencia"""
        fecha_vigencia = self.cleaned_data['fecha_vigencia']
        if fecha_vigencia <= timezone.now().date():
            raise ValidationError('La fecha de vigencia debe ser posterior a hoy.')
        return fecha_vigencia


class SeniaForm(forms.ModelForm):
    """Formulario para gestionar señas"""
    
    class Meta:
        model = Senia
        fields = ['id_evento', 'monto', 'estado']
        widgets = {
            'id_evento': forms.Select(attrs={'class': 'form-select'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean_monto(self):
        """Validar monto de la seña"""
        monto = self.cleaned_data['monto']
        if monto <= 0:
            raise ValidationError('El monto debe ser mayor a 0.')
        return monto


class PersonalForm(forms.ModelForm):
    """Formulario para crear y editar personal"""
    
    class Meta:
        model = Personal
        fields = ['nombre_y_apellido', 'tipo_personal', 'telefono', 'email', 'estado']
        widgets = {
            'nombre_y_apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre y apellido completo'}),
            'tipo_personal': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@email.com'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean_nombre_y_apellido(self):
        """Validar que el nombre y apellido no esté vacío"""
        nombre = self.cleaned_data['nombre_y_apellido']
        if not nombre or len(nombre.strip()) < 3:
            raise ValidationError('El nombre y apellido debe tener al menos 3 caracteres.')
        return nombre.strip()
    
    def clean_telefono(self):
        """Validar formato de teléfono"""
        telefono = self.cleaned_data['telefono']
        if telefono:
            # Remover espacios y caracteres especiales
            telefono_limpio = ''.join(filter(str.isdigit, telefono))
            if len(telefono_limpio) < 8:
                raise ValidationError('El teléfono debe tener al menos 8 dígitos.')
        return telefono
    
    def clean_email(self):
        """Validar formato de email"""
        email = self.cleaned_data['email']
        if email:
            # Verificar que no exista otro personal con el mismo email
            if Personal.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise ValidationError('Ya existe un miembro del personal con este email.')
        return email


class ServicioForm(forms.ModelForm):
    """Formulario para asignar servicios"""
    
    class Meta:
        model = Servicio
        fields = ['id_evento', 'id_personal', 'cantidad_personal', 'estado']
        widgets = {
            'id_evento': forms.Select(attrs={'class': 'form-select'}),
            'id_personal': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_personal': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }


# Formularios de búsqueda y filtros
class ClienteSearchForm(forms.Form):
    """Formulario de búsqueda de clientes"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre, apellido, email o documento...'
        })
    )


class EventoFilterForm(forms.Form):
    """Formulario de filtros para eventos"""
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + EventoSolicitado.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tipo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + EventoSolicitado.TIPO_EVENTO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


class ConsultaFinancieraForm(forms.Form):
    """Formulario para consulta financiera"""
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


# Formularios para asignación de personal
class AsignacionPersonalForm(forms.Form):
    """Formulario para asignar personal a eventos"""
    personal = forms.ModelChoiceField(
        queryset=Personal.objects.filter(estado='ACTIVO'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )
    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        required=False
    )


# Formularios para menús dinámicos
class MenuItemForm(forms.Form):
    """Formulario para items de menú"""
    tipo_producto = forms.ModelChoiceField(
        queryset=TipoProducto.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select menu-tipo'}),
        empty_label="Seleccione un tipo de producto"
    )
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select menu-producto'}),
        empty_label="Seleccione un producto"
    )
    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control menu-cantidad', 'min': '1'}),
        initial=1
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'tipo_producto' in self.data:
            try:
                tipo_id = self.data.get('tipo_producto')
                if tipo_id:
                    tipo_id = int(tipo_id)
                    self.fields['producto'].queryset = Producto.objects.filter(
                        id_tipo_producto_id=tipo_id,
                        disponible=True
                    )
            except (ValueError, TypeError):
                pass


# Formularios para reportes
class ReporteForm(forms.Form):
    """Formulario base para reportes"""
    fecha_inicio = forms.DateField(
        label="Fecha de inicio",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    fecha_fin = forms.DateField(
        label="Fecha de fin",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    formato = forms.ChoiceField(
        choices=[('html', 'HTML'), ('pdf', 'PDF'), ('excel', 'Excel')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='html'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise ValidationError('La fecha de inicio no puede ser posterior a la fecha de fin.')
        
        return cleaned_data


class AsignarPersonalForm(forms.ModelForm):
    """Formulario para asignar personal a eventos"""
    
    class Meta:
        model = Servicio
        fields = ['id_personal', 'cantidad_personal', 'estado']
        widgets = {
            'id_personal': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_personal': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo personal activo
        self.fields['id_personal'].queryset = Personal.objects.filter(estado='ACTIVO')


class CambiarEstadoEventoForm(forms.ModelForm):
    """Formulario para cambiar el estado de un evento"""
    
    class Meta:
        model = EventoSolicitado
        fields = ['estado']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }


class TipoProductoForm(forms.ModelForm):
    """Formulario para crear y editar tipos de productos"""
    
    class Meta:
        model = TipoProducto
        fields = ['descripcion']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción del tipo de producto'}),
        }
    
    def clean_descripcion(self):
        """Validar que la descripción no esté vacía"""
        descripcion = self.cleaned_data['descripcion']
        if not descripcion or len(descripcion.strip()) < 3:
            raise ValidationError('La descripción debe tener al menos 3 caracteres.')
        return descripcion.strip()
