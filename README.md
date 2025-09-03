# 🍽️ Tu Solución - Sistema de Gestión de Catering

Un sistema web completo y profesional para la gestión integral de empresas de catering, desarrollado con Django y tecnologías modernas.

## ✨ Características Principales

### 🎯 **Gestión de Eventos**
- **Reservas completas** con formularios intuitivos
- **Calendario de eventos** con vista organizada
- **Estados de eventos** (Solicitado, Confirmado, En Proceso, Finalizado, Cancelado)
- **Asignación de personal** a eventos específicos
- **Gestión de menús** personalizados por tipo de producto

### 👥 **Gestión de Personas**
- **Clientes** con perfiles completos y usuarios asociados
- **Personal** categorizado por tipo (Mozo, Cocinero, Asistente, Supervisor)
- **Responsables** de servicios con información detallada
- **Sistema de usuarios** con perfiles extendidos

### 📦 **Catálogo de Productos**
- **Productos** con precios, disponibilidad y categorías
- **Tipos de productos** organizados (Bebidas, Entradas, Platos Principales, Postres)
- **Gestión completa** (Crear, Editar, Eliminar, Ver detalles)
- **Filtros avanzados** por tipo y disponibilidad

### 💰 **Gestión Financiera**
- **Comprobantes** automáticos con cálculos de precios
- **Señas** del 30% del total del servicio
- **Precios por persona** calculados automáticamente
- **Reportes financieros** detallados

### 📊 **Reportes y Consultas**
- **Análisis financiero** con métricas clave
- **Análisis por barrios** para marketing geográfico
- **Reporte de cumpleaños** para recordatorios
- **Dashboard** con estadísticas en tiempo real

### 🔐 **Sistema de Usuarios**
- **Autenticación** segura con Django
- **Perfiles extendidos** con información adicional
- **Roles diferenciados** (Admin, Empleado, Responsable, Cliente)
- **Acceso personalizado** según el tipo de usuario

## 🚀 Tecnologías Utilizadas

- **Backend**: Django 4.2+
- **Base de Datos**: MySQL
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Formularios**: Django Crispy Forms + Bootstrap 5
- **Iconos**: Bootstrap Icons
- **Fuentes**: Google Fonts (Inter)
- **Python**: 3.8+

## 📋 Requisitos del Sistema

- Python 3.8 o superior
- MySQL 5.7 o superior
- Navegador web moderno
- 2GB RAM mínimo
- 500MB espacio en disco

## 🛠️ Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd Fieroli
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos
```bash
# Crear base de datos MySQL
mysql -u root -p
CREATE DATABASE tu_solucion CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configurar Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```env
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=mysql://usuario:password@localhost:3306/tu_solucion
```

### 6. Ejecutar Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crear Usuario Administrador
```bash
python manage.py crear_usuario --username admin --email admin@tusolucion.com --first_name Admin --last_name Sistema --tipo ADMIN --superuser
```

### 8. Ejecutar el Servidor
```bash
python manage.py runserver
```

## 📁 Estructura del Proyecto

```
Fieroli/
├── catering/                 # Aplicación principal
│   ├── models.py            # Modelos de datos
│   ├── views.py             # Vistas y lógica de negocio
│   ├── forms.py             # Formularios personalizados
│   ├── urls.py              # Configuración de URLs
│   ├── admin.py             # Panel de administración
│   ├── templates/           # Plantillas HTML
│   └── management/          # Comandos personalizados
├── tu_solucion/             # Configuración del proyecto
│   ├── settings.py          # Configuración principal
│   ├── urls.py              # URLs principales
│   └── wsgi.py              # Configuración WSGI
├── static/                  # Archivos estáticos
│   ├── css/                 # Hojas de estilo
│   ├── js/                  # JavaScript
│   └── images/              # Imágenes
├── templates/               # Plantillas base
├── docs/                    # Documentación
├── Database/                # Scripts de base de datos
└── requirements.txt         # Dependencias Python
```

## 🎮 Uso del Sistema

### **Acceso Inicial**
1. Abrir navegador en `http://localhost:8000`
2. Iniciar sesión con usuario administrador
3. Acceder al dashboard principal

### **Crear un Evento**
1. Ir a **Eventos → Nueva Reserva**
2. Completar formulario con datos del cliente
3. Seleccionar productos del menú
4. Asignar personal necesario
5. Confirmar reserva

### **Gestionar Productos**
1. Ir a **Gestión → Productos**
2. Crear nuevos productos con **Nuevo Producto**
3. Organizar por **Tipos de Producto**
4. Actualizar precios y disponibilidad

### **Asignar Personal**
1. Ir a **Eventos → Ver Eventos**
2. Seleccionar evento específico
3. Hacer clic en **Asignar Personal**
4. Seleccionar personal y cantidad

## 🔧 Comandos Personalizados

### **Crear Usuario**
```bash
python manage.py crear_usuario --username usuario --email email@ejemplo.com --first_name Nombre --last_name Apellido --tipo EMPLEADO
```

### **Tipos de Usuario Disponibles**
- `ADMIN`: Acceso completo al sistema
- `EMPLEADO`: Gestión de eventos y productos
- `RESPONSABLE`: Supervisión de servicios
- `CLIENTE`: Visualización de eventos propios

## 📊 Funcionalidades Avanzadas

### **Sistema de Menús**
- Creación de menús personalizados por evento
- Cálculo automático de precios
- Gestión de cantidades y productos
- Categorización por tipo de producto

### **Gestión de Personal**
- Asignación dinámica a eventos
- Control de disponibilidad
- Seguimiento de servicios
- Estados de asignación

### **Reportes Inteligentes**
- Análisis financiero detallado
- Estadísticas por barrio
- Recordatorios de cumpleaños
- Métricas de rendimiento

## 🎨 Personalización

### **Temas y Estilos**
- Sistema de temas personalizable
- Paleta de colores configurable
- Iconos y fuentes personalizables
- Diseño responsive para móviles

### **Configuración de Empresa**
- Logo y branding personalizable
- Información de contacto editable
- Configuración de horarios
- Políticas de reserva

## 🚨 Solución de Problemas

### **Errores Comunes**

#### **Error de Base de Datos**
```bash
python manage.py check
python manage.py migrate
```

#### **Problemas de Dependencias**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### **Errores de Pylance/VS Code**
- Los archivos de configuración ya están optimizados
- Reiniciar VS Code después de cambios
- Verificar que el entorno virtual esté activado

## 📈 Roadmap Futuro

### **Versión 2.0**
- [ ] API REST completa
- [ ] Aplicación móvil nativa
- [ ] Integración con sistemas de pago
- [ ] Notificaciones push

### **Versión 2.1**
- [ ] Dashboard avanzado con gráficos
- [ ] Sistema de inventario
- [ ] Gestión de proveedores
- [ ] Reportes automáticos por email

### **Versión 2.2**
- [ ] Inteligencia artificial para precios
- [ ] Predicción de demanda
- [ ] Optimización de rutas
- [ ] Integración con redes sociales

## 🤝 Contribución

1. Fork del proyecto
2. Crear rama para nueva funcionalidad
3. Commit de cambios
4. Push a la rama
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 📞 Soporte

- **Email**: soporte@tusolucion.com
- **Documentación**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/tusolucion/fieroli/issues)

## 🙏 Agradecimientos

- **Django Community** por el framework excepcional
- **Bootstrap Team** por el diseño responsive
- **Contribuidores** que han ayudado al proyecto

---

**Desarrollado con ❤️ por Tu Solución**

*Sistema profesional de gestión de catering que transforma la manera de administrar eventos*
