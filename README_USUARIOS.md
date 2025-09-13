# 🔐 Credenciales de Usuario - Tu Solución

## 📋 Resumen de Usuarios del Sistema

Este documento contiene todas las credenciales de acceso para los diferentes tipos de usuarios del sistema de gestión de catering "Tu Solución".

---

## 👑 **ADMINISTRADORES**

Los administradores tienen acceso completo al sistema, pueden crear eventos, gestionar usuarios, productos y personal.

### 🔑 **Credenciales de Administrador:**

| Usuario | Contraseña | Nombre | Email | Funciones |
|---------|------------|--------|-------|-----------|
| `admin` | `admin123` | Administrador | admin@tusolucion.com | Superusuario principal |
| `admin2` | `TuSolucion2024!` | Roberto Martínez | admin2@tusolucion.com | Administrador secundario |

**Acceso:** 
- Panel de administración: `/dashboard/`
- Django Admin: `/admin/`

---

## 👨‍💼 **RESPONSABLES**

Los responsables gestionan eventos asignados por el administrador, pueden asignar personal y productos, pero NO pueden crear eventos.

### 🔑 **Credenciales de Responsable:**

| Usuario | Contraseña | Nombre | Email | Funciones |
|---------|------------|--------|-------|-----------|
| `carlos.rodriguez_2` | `responsable123` | Carlos Rodríguez | carlos.rodriguez@tusolucion.com | Responsable de eventos |
| `maria.gonzalez_1` | `responsable123` | María González | maria.gonzalez@tusolucion.com | Responsable de eventos |
| `responsable1` | `TuSolucion2024!` | Ana López | responsable1@tusolucion.com | Responsable de ejemplo |

**Acceso:** 
- Dashboard responsable: `/responsable/dashboard/`
- **Pueden:** Asignar personal, gestionar productos, editar menús, cambiar estados de eventos
- **NO pueden:** Crear eventos (solo el admin)

---

## 👷 **EMPLEADOS/TRABAJADORES**

Los empleados solo pueden ver los detalles de los eventos donde están asignados para trabajar.

### 🔑 **Credenciales de Empleado:**

| Usuario | Contraseña | Nombre | Email | Funciones |
|---------|------------|--------|-------|-----------|
| `luis.fernandez_3` | `empleado123` | Luis Fernández | luis.fernandez@tusolucion.com | Empleado de cocina |
| `ana.martinez_2` | `empleado123` | Ana Martínez | ana.martinez@tusolucion.com | Empleada de servicio |
| `juan.perez_1` | `empleado123` | Juan Pérez | juan.perez@tusolucion.com | Empleado de cocina |
| `empleado1` | `TuSolucion2024!` | María González | empleado1@tusolucion.com | Empleada de ejemplo |
| `empleado2` | `TuSolucion2024!` | Carlos Rodríguez | empleado2@tusolucion.com | Empleado de ejemplo |

**Acceso:** 
- Dashboard empleado: `/empleado/dashboard/`
- **Pueden:** Ver detalles de eventos asignados, ver menús, ver información del cliente
- **NO pueden:** Crear eventos, asignar personal, gestionar productos

---

## 👤 **CLIENTES**

Los clientes pueden registrarse y ver sus eventos, pero no pueden crear eventos directamente.

### 🔑 **Credenciales de Cliente:**

| Usuario | Contraseña | Nombre | Email | Funciones |
|---------|------------|--------|-------|-----------|
| `cliente1` | `cliente123` | Juan Pérez | juan.perez@cliente.com | Cliente registrado |
| `cliente2` | `cliente123` | María García | maria.garcia@cliente.com | Cliente registrado |
| `cliente3` | `cliente123` | Carlos López | carlos.lopez@cliente.com | Cliente registrado |

**Acceso:** 
- Dashboard cliente: `/cliente/dashboard/`
- **Pueden:** Ver sus eventos, ver historial de pagos, registrarse
- **NO pueden:** Crear eventos, acceder a paneles administrativos

---

## 🌐 **URLs de Acceso**

### 📊 **Dashboards:**
- **Admin:** `http://localhost:8000/dashboard/`
- **Responsable:** `http://localhost:8000/responsable/dashboard/`
- **Empleado:** `http://localhost:8000/empleado/dashboard/`
- **Cliente:** `http://localhost:8000/cliente/dashboard/`

### 🔧 **Administración:**
- **Django Admin:** `http://localhost:8000/admin/`
- **Login:** `http://localhost:8000/accounts/login/`
- **Registro:** `http://localhost:8000/accounts/registro/`

---

## 🎯 **Reglas de Negocio por Rol**

### 👑 **ADMINISTRADOR:**
- ✅ Crear, editar y eliminar eventos
- ✅ Gestionar usuarios (crear, editar, eliminar)
- ✅ Gestionar productos y tipos de productos
- ✅ Gestionar personal
- ✅ Asignar responsables a eventos
- ✅ Ver todas las consultas y reportes
- ✅ Acceso completo al sistema

### 👨‍💼 **RESPONSABLE:**
- ❌ **NO puede crear eventos** (solo el admin)
- ✅ Gestionar eventos asignados por el admin
- ✅ Asignar personal a eventos
- ✅ Gestionar productos y menús
- ✅ Cambiar estados de eventos
- ✅ Gestionar señas de eventos
- ✅ Ver eventos asignados

### 👷 **EMPLEADO:**
- ❌ **NO puede crear eventos**
- ❌ **NO puede asignar personal**
- ❌ **NO puede gestionar productos**
- ✅ Ver detalles de eventos donde está asignado
- ✅ Ver menús de eventos asignados
- ✅ Ver información del cliente
- ✅ Solo lectura de eventos asignados

### 👤 **CLIENTE:**
- ❌ **NO puede crear eventos**
- ❌ **NO puede acceder a paneles administrativos**
- ✅ Ver sus propios eventos
- ✅ Ver historial de pagos
- ✅ Registrarse en el sistema
- ✅ Ver detalles de sus eventos confirmados

---

## 🚀 **Cómo Iniciar el Sistema**

1. **Iniciar el servidor:**
   ```bash
   python manage.py runserver
   ```

2. **Acceder al sistema:**
   - Ir a: `http://localhost:8000`
   - Usar las credenciales de la tabla correspondiente

3. **Para desarrollo:**
   - Django Admin: `http://localhost:8000/admin/`
   - Usuario: `admin` / Contraseña: `admin123`

---

## 📝 **Notas Importantes**

- 🔒 **Cambiar contraseñas:** Se recomienda cambiar las contraseñas por defecto en producción
- 👥 **Crear usuarios:** Los clientes pueden registrarse automáticamente
- 🔄 **Roles:** Los roles están definidos en el modelo `PerfilUsuario`
- 📊 **Dashboards:** Cada tipo de usuario tiene su dashboard específico
- 🎯 **Permisos:** Los permisos están controlados por decoradores en las vistas

---

## 🆘 **Soporte**

Si tienes problemas con el acceso:
1. Verificar que el servidor esté ejecutándose
2. Comprobar que las credenciales sean correctas
3. Revisar los logs del servidor Django
4. Contactar al administrador del sistema

---

**Sistema desarrollado para Tu Solución - Gestión Integral de Catering** 🍽️
