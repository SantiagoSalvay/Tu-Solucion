# Sistema de Gestión de Catering - Tu Solución

## Descripción del Proyecto

**Tu Solución** es una empresa de catering ubicada en la ciudad de Córdoba que ofrece servicios de preparación y servicio de comida y bebida en eventos en el domicilio indicado por el cliente.

Este sistema de información permite gestionar el alquiler y realización del servicio de catering, incluyendo la gestión de clientes, eventos, menús, personal, pagos y consultas administrativas.

## Características del Sistema

### Funcionalidades Principales

1. **Home y Navegación**
   - Acceso a todas las páginas del sistema
   - Dashboard con estadísticas en tiempo real
   - Navegación intuitiva con menús desplegables

2. **Sistema de Autenticación**
   - Login y registro de usuarios
   - Gestión de sesiones
   - Control de acceso a funcionalidades

3. **Reserva de Catering (Transacción Principal)**
   - Proceso completo de reserva con verificación de disponibilidad
   - Selección de cliente, tipo de evento, fecha y ubicación
   - Validación automática de disponibilidad (máximo 10 eventos por día)

4. **Gestión de Clientes**
   - Registro y consulta de clientes
   - Datos personales completos (nombre, apellido, documento, email, domicilio, fecha de nacimiento)
   - Historial de servicios contratados
   - Búsqueda y filtrado avanzado

5. **Gestión de Eventos**
   - **Visualización completa** de todos los eventos programados
   - **Edición completa** de eventos (modificar todos los datos incluyendo precios)
   - **Eliminación** de eventos con validaciones de seguridad
   - Control de estados del evento (solicitado, confirmado, en proceso, finalizado, cancelado, vencido)
   - Filtros por estado, tipo, fecha y ubicación

6. **Gestión de Menús**
   - Catálogo de productos por tipo (bebidas, entradas, platos principales, postres)
   - **Armado personalizado de menús** por evento
   - **Edición de menús** con agregado/eliminación de productos
   - Cálculo automático de precios por producto y total del servicio
   - Precio por persona calculado automáticamente

7. **Gestión de Pagos**
   - Sistema de seña (30% del total) con plazo de 10 días
   - Control de pagos en efectivo
   - Generación de comprobantes y recibos
   - Facturación final del servicio

8. **Gestión de Personal**
   - Asignación de personal por evento (mozos, cocineros, asistentes)
   - Control de disponibilidad y estados
   - Notificaciones de asignación

9. **Consultas Administrativas Específicas**
   - **Consulta Financiera**: Costo total de productos por servicio (últimos 3 meses, cantidad entre 200-500)
   - **Análisis de Barrios**: Top 10 barrios más solicitados en Buenos Aires (solo eventos finalizados)
   - **Reporte de Cumpleaños**: Clientes con cumpleaños en el mes actual (nombre con vocal como segunda letra)

## Tecnologías Utilizadas

- **Backend**: Django 4.2+
- **Base de Datos**: MySQL 8.0+
- **Lenguaje**: Python 3.8+
- **Frontend**: HTML, CSS, JavaScript (Bootstrap 5)
- **Autenticación**: Django Authentication System
- **Formularios**: Django Crispy Forms con Bootstrap 5
- **API**: Django REST Framework
- **Validación**: Validación del lado cliente y servidor

## Estructura del Proyecto

```
tu_solucion/
├── manage.py
├── requirements.txt
├── tu_solucion/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── catering/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   └── migrations/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── base.html
│   ├── catering/
│   └── registration/
├── docs/
│   ├── er.mmd
│   └── uml/
└── README.md
```

## Instalación y Configuración

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (para clonar el repositorio)
- MySQL 8.0 o superior
- MySQL Workbench (recomendado para gestión de base de datos)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd tu_solucion
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar la base de datos MySQL**
   
   a. Crear la base de datos en MySQL:
   ```sql
   CREATE DATABASE tu_solucion CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
   
   b. Configurar las credenciales en `tu_solucion/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'tu_solucion',
           'USER': 'tu_usuario',
           'PASSWORD': 'tu_password',
           'HOST': 'localhost',
           'PORT': '3306',
       }
   }
   ```
   
   c. Ejecutar las migraciones:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Crear superusuario**
   ```bash
   python manage.py createsuperuser
   ```

6. **Ejecutar el servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

7. **Acceder al sistema**
   - URL principal: http://127.0.0.1:8000/
   - Panel de administración: http://127.0.0.1:8000/admin/

### Funcionalidades Implementadas

#### Reserva de Catering
- **URL**: `/reserva/`
- **Descripción**: Proceso completo de reserva de catering
- **Características**:
  - Selección de cliente y responsable
  - Verificación automática de disponibilidad
  - Configuración de fecha, hora y ubicación
  - Creación automática de comprobante

#### Gestión de Menús
- **URL**: `/eventos/<id>/editar-menu/`
- **Descripción**: Edición completa de menús por evento
- **Características**:
  - Agregar productos por tipo
  - Eliminar productos del menú
  - Cálculo automático de precios
  - Actualización en tiempo real

#### Lista de Eventos
- **URL**: `/eventos/`
- **Descripción**: Visualización completa de todos los eventos
- **Características**:
  - Filtros por estado, tipo y fecha
  - Paginación
  - Acciones: Ver, Editar, Editar Menú, Eliminar
  - Información de precios

#### Consultas Específicas
- **Consulta Financiera**: `/consultas/financiera/`
- **Análisis de Barrios**: `/consultas/barrios/`
- **Reporte de Cumpleaños**: `/consultas/cumpleanos/`

## Configuración del Entorno

### Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Configuración de Base de Datos

El sistema utiliza SQLite3 por defecto. La base de datos se creará automáticamente en `db.sqlite3` al ejecutar las migraciones.

## Uso del Sistema

### Roles de Usuario

1. **Responsable de Servicios**
   - Gestión de clientes y eventos
   - Consulta de disponibilidad
   - Armado de menús
   - Asignación de personal

2. **Responsable de Cobro**
   - Gestión de pagos y señas
   - Generación de comprobantes
   - Facturación final

3. **Encargado de Compras**
   - Consulta de servicios confirmados
   - Gestión de proveedores
   - Control de inventario

4. **Administrador**
   - Acceso completo al sistema
   - Gestión de usuarios
   - Configuración del sistema

### Flujo de Trabajo Principal

1. **Solicitud de Servicio**
   - Cliente solicita servicio de catering
   - Responsable consulta disponibilidad
   - Registro o verificación de datos del cliente

2. **Definición del Evento**
   - Especificación de fecha, hora, ubicación
   - Definición del tipo de evento
   - Armado del menú personalizado

3. **Confirmación y Pago**
   - Generación del comprobante
   - Pago de seña (30% del total)
   - Confirmación del servicio

4. **Preparación del Evento**
   - Asignación de personal
   - Gestión de compras
   - Preparación de productos

5. **Ejecución del Servicio**
   - Realización del evento
   - Pago del saldo
   - Facturación final

## Consultas del Sistema

### Consulta Financiera
- **Objetivo**: Calcular costo total de productos por servicio
- **Filtros**: Últimos 3 meses, cantidad de productos entre 200-500
- **Acceso**: Área de Finanzas

### Consulta de Marketing - Barrios
- **Objetivo**: Top 10 barrios más solicitados
- **Filtros**: Solo barrios de Buenos Aires, servicios finalizados
- **Información**: Cantidad de servicios y servicio de mayor costo por barrio

### Consulta de Marketing - Cumpleaños
- **Objetivo**: Clientes con cumpleaños en el mes actual
- **Filtros**: Nombre con vocal como segunda letra
- **Información**: Edad y monto total cobrado

## Modelos de Datos

### Entidades Principales

- **Clientes**: Información personal y de contacto
- **Eventos**: Detalles del evento solicitado
- **Menús**: Productos y cantidades por evento
- **Personal**: Empleados y sus roles
- **Pagos**: Control de señas y pagos finales
- **Servicios**: Asignación de personal por evento

### Relaciones

- Un cliente puede tener múltiples eventos
- Un evento tiene un menú específico
- Un evento puede tener múltiples servicios (personal asignado)
- Un menú contiene múltiples productos

## API Endpoints

### Clientes
- `GET /api/clientes/` - Listar clientes
- `POST /api/clientes/` - Crear cliente
- `GET /api/clientes/{id}/` - Obtener cliente específico
- `PUT /api/clientes/{id}/` - Actualizar cliente

### Eventos
- `GET /api/eventos/` - Listar eventos
- `POST /api/eventos/` - Crear evento
- `GET /api/eventos/{id}/` - Obtener evento específico
- `PUT /api/eventos/{id}/` - Actualizar evento

### Menús
- `GET /api/menus/` - Listar menús
- `POST /api/menus/` - Crear menú
- `GET /api/menus/{id}/` - Obtener menú específico

## Seguridad

- Autenticación basada en sesiones
- Autorización por roles
- Validación de formularios
- Protección CSRF
- Sanitización de datos

## Mantenimiento

### Backup de Base de Datos
```bash
python manage.py dumpdata > backup.json
```

### Restaurar Base de Datos
```bash
python manage.py loaddata backup.json
```

### Actualizar Dependencias
```bash
pip install --upgrade -r requirements.txt
```

## Desarrollo

### Estructura de Código
- **Models**: Definición de entidades y relaciones
- **Views**: Lógica de negocio y presentación
- **Forms**: Validación de datos de entrada
- **Templates**: Interfaz de usuario
- **URLs**: Enrutamiento de la aplicación

### Convenciones de Código
- PEP 8 para Python
- Nombres descriptivos para variables y funciones
- Documentación en docstrings
- Comentarios explicativos donde sea necesario

## Testing

### Ejecutar Tests
```bash
python manage.py test
```

### Cobertura de Tests
```bash
coverage run --source='.' manage.py test
coverage report
```

## Despliegue

### Producción
1. Configurar `DEBUG=False`
2. Configurar base de datos de producción
3. Configurar servidor web (Nginx/Apache)
4. Configurar WSGI (Gunicorn/uWSGI)
5. Configurar variables de entorno de producción

### Docker (Opcional)
```bash
docker build -t tu-solucion .
docker run -p 8000:8000 tu-solucion
```

## Soporte

### Contacto
- **Desarrollador**: [Tu Nombre]
- **Email**: [tu-email@ejemplo.com]
- **Documentación**: [URL de documentación]

### Issues y Bug Reports
- Crear issue en el repositorio de GitHub
- Incluir descripción detallada del problema
- Adjuntar logs y capturas de pantalla si es necesario

## Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

## Changelog

### v1.0.0 (2024-01-XX)
- Versión inicial del sistema
- Gestión completa de clientes, eventos y menús
- Sistema de pagos y facturación
- Consultas administrativas
- Panel de administración

---

**Tu Solución** - Sistema de Gestión de Catering
Desarrollado con Django y Python