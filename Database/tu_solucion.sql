DROP DATABASE IF exists tu_solucion;
CREATE DATABASE IF NOT EXISTS tu_solucion;
USE tu_solucion;

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS tu_solucion;
USE tu_solucion;

-- Tabla clientes
CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    tipo_doc VARCHAR(10) NOT NULL,
    num_doc VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    domicilio VARCHAR(200) NOT NULL,
    fecha_alta DATE NOT NULL,
    fecha_nacimiento DATE NULL
);

-- Tabla responsable
CREATE TABLE responsable (
    id_responsable INT AUTO_INCREMENT PRIMARY KEY,
    nombre_apellido VARCHAR(200) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- Tabla tipo_productos
CREATE TABLE tipo_productos (
    id_tipo_producto INT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL
);

-- Tabla productos_x_tipo
CREATE TABLE productos_x_tipo (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    id_tipo_producto INT NOT NULL,
    descripcion VARCHAR(200) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    disponible BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_tipo_producto) REFERENCES tipo_productos(id_tipo_producto)
);

-- Tabla evento_solicitado
CREATE TABLE evento_solicitado (
    id_evento INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_responsable INT NOT NULL,
    tipo_evento ENUM('CASAMIENTO', 'CUMPLEAÑOS', 'EVENTO_COMERCIAL') NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    ubicacion VARCHAR(200) NOT NULL,
    cantidad_personas INT NOT NULL,
    estado ENUM('SOLICITADO', 'CONFIRMADO', 'EN_PROCESO', 'FINALIZADO', 'CANCELADO', 'VENCIDO') DEFAULT 'SOLICITADO',
    precio_total DECIMAL(10,2) DEFAULT 0.00,
    precio_por_persona DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_responsable) REFERENCES responsable(id_responsable)
);

-- Tabla comprobante
CREATE TABLE comprobante (
    id_comprobante INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_evento INT NOT NULL,
    fecha_pedido DATE NOT NULL,
    importe_total_productos DECIMAL(10,2) NOT NULL,
    total_servicio DECIMAL(10,2) NOT NULL,
    precio_x_persona DECIMAL(10,2) NOT NULL,
    fecha_vigencia DATE NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (id_evento) REFERENCES evento_solicitado(id_evento)
);

-- Tabla menu_x_tipo_producto
CREATE TABLE menu_x_tipo_producto (
    id_menu INT AUTO_INCREMENT PRIMARY KEY,
    id_evento INT NOT NULL,
    id_tipo_producto INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad_producto INT NOT NULL,
    precio_uni DECIMAL(10,2) NOT NULL,
    precio_total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_evento) REFERENCES evento_solicitado(id_evento),
    FOREIGN KEY (id_tipo_producto) REFERENCES tipo_productos(id_tipo_producto),
    FOREIGN KEY (id_producto) REFERENCES productos_x_tipo(id_producto)
);

-- Tabla senia
CREATE TABLE senia (
    id_senia INT AUTO_INCREMENT PRIMARY KEY,
    id_evento INT NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    estado ENUM('PENDIENTE', 'PAGADA', 'VENCIDA') DEFAULT 'PENDIENTE',
    fecha_pago DATE NULL,
    FOREIGN KEY (id_evento) REFERENCES evento_solicitado(id_evento)
);

-- Tabla personal
CREATE TABLE personal (
    id_personal INT AUTO_INCREMENT PRIMARY KEY,
    tipo_personal ENUM('MOZO', 'COCINERO', 'ASISTENTE') NOT NULL,
    nombre_y_apellido VARCHAR(200) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    estado ENUM('ACTIVO', 'INACTIVO') DEFAULT 'ACTIVO'
);

-- Tabla servicios
CREATE TABLE servicios (
    id_servicio INT AUTO_INCREMENT PRIMARY KEY,
    id_evento INT NOT NULL,
    id_personal INT NOT NULL,
    cantidad_personal INT NOT NULL,
    estado ENUM('ASIGNADO', 'EN_PROCESO', 'COMPLETADO') DEFAULT 'ASIGNADO',
    FOREIGN KEY (id_evento) REFERENCES evento_solicitado(id_evento),
    FOREIGN KEY (id_personal) REFERENCES personal(id_personal)
);

-- Tabla usuarios (para el sistema de login)
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    is_staff BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL
);	

-- Índices para mejorar rendimiento
CREATE INDEX idx_evento_fecha ON evento_solicitado(fecha);
CREATE INDEX idx_evento_estado ON evento_solicitado(estado);
CREATE INDEX idx_cliente_email ON clientes(email);
CREATE INDEX idx_menu_evento ON menu_x_tipo_producto(id_evento);
CREATE INDEX idx_senia_evento ON senia(id_evento);
CREATE INDEX idx_servicios_evento ON servicios(id_evento);