from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from .models import (
    Cliente, Responsable, TipoProducto, Producto, Comprobante,
    EventoSolicitado, MenuXTipoProducto, Senia, Personal, Servicio, PerfilUsuario,
    Provincia, Barrio
)

class ClienteForm(forms.ModelForm):
    """Formulario para crear y editar clientes"""

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
        fields = ['id_cliente', 'id_responsable', 'tipo_evento', 'fecha', 'hora', 'ubicacion', 'cantidad_personas', 
                 'tiene_sena', 'monto_sena', 'fecha_sena', 'observaciones_sena']
        widgets = {
            'id_cliente': forms.Select(attrs={'class': 'form-select'}),
            'id_responsable': forms.Select(attrs={'class': 'form-select'}),
            'tipo_evento': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección completa del evento'}),
            'cantidad_personas': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'tiene_sena': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'monto_sena': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'fecha_sena': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones_sena': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observaciones sobre la seña...'}),
        }
    
    def clean_fecha(self):
        """Validar que la fecha no sea anterior a hoy"""
        fecha = self.cleaned_data['fecha']
        if fecha < timezone.now().date():
            raise ValidationError('La fecha del evento no puede ser anterior a hoy.')
        return fecha
    
    def clean(self):
        """Validaciones cruzadas para los campos de seña"""
        cleaned_data = super().clean()
        tiene_sena = cleaned_data.get('tiene_sena')
        monto_sena = cleaned_data.get('monto_sena')
        fecha_sena = cleaned_data.get('fecha_sena')
        
        if tiene_sena:
            if not monto_sena or monto_sena <= 0:
                raise ValidationError('Si el cliente dejó seña, debe especificar un monto válido.')
            
            if not fecha_sena:
                raise ValidationError('Si el cliente dejó seña, debe especificar la fecha.')

            if fecha_sena > timezone.now().date():
                raise ValidationError('La fecha de la seña no puede ser futura.')
        else:

            cleaned_data['monto_sena'] = None
            cleaned_data['fecha_sena'] = None
            cleaned_data['observaciones_sena'] = ''
        
        return cleaned_data

class EventoResponsableForm(forms.ModelForm):
    """Formulario específico para responsables - solo pueden editar cantidad de personal"""
    
    class Meta:
        model = EventoSolicitado
        fields = ['cantidad_personas']
        widgets = {
            'cantidad_personas': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '1',
                'placeholder': 'Ingrese la cantidad de personas'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cantidad_personas'].label = 'Cantidad de Personas'
        self.fields['cantidad_personas'].help_text = 'Número total de personas que asistirán al evento'

class GestionarSenaForm(forms.ModelForm):
    """Formulario para que los responsables gestionen la seña de un evento"""
    
    class Meta:
        model = EventoSolicitado
        fields = ['tiene_sena', 'monto_sena', 'fecha_sena', 'observaciones_sena']
        widgets = {
            'tiene_sena': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_tiene_sena'
            }),
            'monto_sena': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'id': 'id_monto_sena',
                'placeholder': '0.00'
            }),
            'fecha_sena': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'id_fecha_sena'
            }),
            'observaciones_sena': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones sobre la seña...',
                'id': 'id_observaciones_sena'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tiene_sena'].label = '¿El cliente dejó seña?'
        self.fields['monto_sena'].label = 'Monto de la Seña ($)'
        self.fields['fecha_sena'].label = 'Fecha de la Seña'
        self.fields['observaciones_sena'].label = 'Observaciones'

        if not self.instance.pk or not self.instance.fecha_sena:
            self.fields['fecha_sena'].initial = timezone.now().date()
    
    def clean(self):
        """Validaciones para los campos de seña"""
        cleaned_data = super().clean()
        tiene_sena = cleaned_data.get('tiene_sena')
        monto_sena = cleaned_data.get('monto_sena')
        fecha_sena = cleaned_data.get('fecha_sena')
        
        if tiene_sena:
            if not monto_sena or monto_sena <= 0:
                raise ValidationError('Si el cliente dejó seña, debe especificar un monto válido.')
            
            if not fecha_sena:
                raise ValidationError('Si el cliente dejó seña, debe especificar la fecha.')

            if fecha_sena > timezone.now().date():
                raise ValidationError('La fecha de la seña no puede ser futura.')
        else:

            cleaned_data['monto_sena'] = None
            cleaned_data['fecha_sena'] = None
            cleaned_data['observaciones_sena'] = ''
        
        return cleaned_data

class AsignarPersonalForm(forms.ModelForm):
    """Formulario para asignar personal a un evento"""
    
    class Meta:
        model = Servicio
        fields = ['id_personal', 'cantidad_personal']
        widgets = {
            'id_personal': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'cantidad_personal': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1',
                'required': True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_personal'].label = 'Personal'
        self.fields['id_personal'].empty_label = "Seleccione un miembro del personal"
        self.fields['id_personal'].queryset = Personal.objects.filter(estado='ACTIVO')
        self.fields['cantidad_personal'].label = 'Cantidad'
        self.fields['cantidad_personal'].help_text = 'Número de personas de este personal asignadas'

class TrabajadorEventoForm(forms.Form):
    """Formulario para agregar trabajadores al evento durante la creación"""
    
    trabajador = forms.ModelChoiceField(
        queryset=Personal.objects.filter(estado='ACTIVO'),
        empty_label="Seleccione un trabajador",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        label='Trabajador'
    )
    
    cantidad = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'value': '1',
            'required': True
        }),
        label='Cantidad',
        help_text='Número de personas de este trabajador asignadas'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['trabajador'].queryset = Personal.objects.filter(estado='ACTIVO')
    
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
            'id_tipo_producto': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'id_id_tipo_producto',
                'required': True
            }),
            'id_producto': forms.Select(attrs={
                'class': 'form-select', 
                'id': 'id_id_producto',
                'required': True
            }),
            'cantidad_producto': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '1',
                'value': '1',
                'required': True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['id_tipo_producto'].empty_label = "Seleccione un tipo de producto"
        self.fields['id_producto'].empty_label = "Seleccione un tipo de producto primero"

        if 'data' in kwargs and kwargs['data']:
            tipo_id = kwargs['data'].get('id_tipo_producto')
            if tipo_id:
                self.fields['id_producto'].queryset = Producto.objects.filter(
                    id_tipo_producto_id=tipo_id, 
                    disponible=True
                )
            else:
                self.fields['id_producto'].queryset = Producto.objects.none()
        else:

            self.fields['id_producto'].queryset = Producto.objects.filter(disponible=True)
        
        self.fields['cantidad_producto'].initial = 1
    
    def clean(self):
        """Validación personalizada del formulario"""
        cleaned_data = super().clean()
        id_tipo_producto = cleaned_data.get('id_tipo_producto')
        id_producto = cleaned_data.get('id_producto')

        if id_tipo_producto and id_producto:
            if id_producto.id_tipo_producto != id_tipo_producto:
                raise ValidationError('El producto seleccionado no pertenece al tipo de producto elegido.')
        
        return cleaned_data

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

            telefono_limpio = ''.join(filter(str.isdigit, telefono))
            if len(telefono_limpio) < 8:
                raise ValidationError('El teléfono debe tener al menos 8 dígitos.')
        return telefono
    
    def clean_email(self):
        """Validar formato de email"""
        email = self.cleaned_data['email']
        if email:

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

class RegistroForm(forms.Form):
    """Formulario para registro de nuevos usuarios (clientes)"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        }),
        help_text='Requerido. 150 caracteres o menos. Solo letras, números y @/./+/-/_'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        })
    )
    password1 = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        help_text='Mínimo 8 caracteres'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    )
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    apellido = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    tipo_doc = forms.ChoiceField(
        choices=[('DNI', 'DNI'), ('PASAPORTE', 'Pasaporte'), ('CEDULA', 'Cédula')],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    num_doc = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de documento'
        })
    )
    provincia = forms.ModelChoiceField(
        queryset=Provincia.objects.filter(activa=True),
        empty_label="Seleccione una provincia",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_provincia'
        })
    )
    barrio = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_barrio',
            'placeholder': 'Ingrese el nombre del barrio'
        }),
        help_text='Nombre del barrio donde reside'
    )
    domicilio = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dirección completa'
        }),
        help_text='Dirección completa de residencia'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Ya existe un usuario con este nombre de usuario.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un usuario con este correo electrónico.')
        return email
    
    def clean_num_doc(self):
        num_doc = self.cleaned_data.get('num_doc')
        if Cliente.objects.filter(num_doc=num_doc).exists():
            raise ValidationError('Ya existe un cliente con este número de documento.')
        return num_doc
    
    def clean_barrio(self):
        barrio = self.cleaned_data.get('barrio')
        if barrio:
            return barrio.strip()
        return barrio
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data

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

class CrearUsuarioForm(forms.Form):
    """Formulario para crear usuarios administrativos"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        help_text='Requerido. 150 caracteres o menos. Solo letras, números y @/./+/-/_.'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@email.com'})
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        help_text='Mínimo 8 caracteres.'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'})
    )
    tipo_usuario = forms.ChoiceField(
        choices=PerfilUsuario.TIPO_USUARIO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    estado = forms.ChoiceField(
        choices=PerfilUsuario.ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='ACTIVO'
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono (opcional)'})
    )
    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    direccion = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección (opcional)'})
    )
    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales (opcional)'})
    )
    
    def clean_username(self):
        username = self.cleaned_data['username']
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            raise ValidationError('Ya existe un usuario con este nombre de usuario.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        from django.contrib.auth.models import User
        if User.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un usuario con este email.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data

class CrearTrabajadorForm(forms.Form):
    """Formulario para crear trabajadores"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        help_text='Requerido. 150 caracteres o menos.'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@email.com'})
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        help_text='Mínimo 8 caracteres.'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    )
    nombre_y_apellido = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre y apellido completo'})
    )
    tipo_personal = forms.ChoiceField(
        choices=Personal.TIPO_PERSONAL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    telefono = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono'})
    )
    estado = forms.ChoiceField(
        choices=Personal.ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='ACTIVO'
    )
    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    direccion = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección (opcional)'})
    )
    
    def clean_username(self):
        username = self.cleaned_data['username']
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            raise ValidationError('Ya existe un usuario con este nombre de usuario.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        from django.contrib.auth.models import User
        if User.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un usuario con este email.')
        if Personal.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un trabajador con este email.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data

class CrearClienteForm(forms.Form):
    """Formulario para crear clientes con cuenta de usuario"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        help_text='Requerido. 150 caracteres o menos.'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@email.com'})
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        help_text='Mínimo 8 caracteres.'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    )
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    apellido = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'})
    )
    tipo_doc = forms.ChoiceField(
        choices=Cliente._meta.get_field('tipo_doc').choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    num_doc = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de documento'})
    )
    domicilio = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Domicilio completo'})
    )
    fecha_nacimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono (opcional)'})
    )
    
    def clean_username(self):
        username = self.cleaned_data['username']
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            raise ValidationError('Ya existe un usuario con este nombre de usuario.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        from django.contrib.auth.models import User
        if User.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un usuario con este email.')
        if Cliente.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un cliente con este email.')
        return email
    
    def clean_num_doc(self):
        num_doc = self.cleaned_data['num_doc']
        if Cliente.objects.filter(num_doc=num_doc).exists():
            raise ValidationError('Ya existe un cliente con este número de documento.')
        return num_doc
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data

class CrearResponsableForm(forms.Form):
    """Formulario para crear responsables con cuenta de usuario"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        help_text='Requerido. 150 caracteres o menos.'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@email.com'})
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        help_text='Mínimo 8 caracteres.'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    )
    nombre_apellido = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre y apellido completo'})
    )
    telefono = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono'})
    )
    direccion = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección (opcional)'})
    )
    
    def clean_username(self):
        username = self.cleaned_data['username']
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            raise ValidationError('Ya existe un usuario con este nombre de usuario.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data['email']
        from django.contrib.auth.models import User
        if User.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un usuario con este email.')
        if Responsable.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un responsable con este email.')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError('Las contraseñas no coinciden.')
        
        return cleaned_data
