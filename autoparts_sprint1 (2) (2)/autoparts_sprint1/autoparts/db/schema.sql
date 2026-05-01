-- ============================================================
--  AutoParts Express - Esquema de Base de Datos - Sprint 1
--  Módulo: Seguridad + Inventario + Ventas
-- ============================================================

-- Roles del sistema
CREATE TABLE IF NOT EXISTS roles (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(50) UNIQUE NOT NULL,  -- 'Vendedor', 'Inventario', 'Gerencia'
    descripcion TEXT
);

-- Usuarios del sistema
CREATE TABLE IF NOT EXISTS usuarios (
    id              SERIAL PRIMARY KEY,
    cedula          VARCHAR(20) UNIQUE NOT NULL,
    nombre          VARCHAR(100) NOT NULL,
    username        VARCHAR(50) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    rol_id          INTEGER REFERENCES roles(id),
    activo          BOOLEAN DEFAULT TRUE,
    intentos_fallidos INTEGER DEFAULT 0,
    bloqueado       BOOLEAN DEFAULT FALSE,
    creado_en       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sesiones activas (auditoría)
CREATE TABLE IF NOT EXISTS sesiones (
    id          SERIAL PRIMARY KEY,
    usuario_id  INTEGER REFERENCES usuarios(id),
    inicio      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fin         TIMESTAMP,
    ip          VARCHAR(45)
);

-- Categorías de productos
CREATE TABLE IF NOT EXISTS categorias (
    id      SERIAL PRIMARY KEY,
    nombre  VARCHAR(100) UNIQUE NOT NULL
);

-- Productos / Inventario
CREATE TABLE IF NOT EXISTS productos (
    id              SERIAL PRIMARY KEY,
    codigo          VARCHAR(50) UNIQUE NOT NULL,
    nombre          VARCHAR(150) NOT NULL,
    descripcion     TEXT,
    categoria_id    INTEGER REFERENCES categorias(id),
    precio_unitario NUMERIC(12, 2) NOT NULL CHECK (precio_unitario >= 0),
    stock_actual    INTEGER NOT NULL DEFAULT 0 CHECK (stock_actual >= 0),
    stock_minimo    INTEGER NOT NULL DEFAULT 0,
    activo          BOOLEAN DEFAULT TRUE,
    creado_en       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id          SERIAL PRIMARY KEY,
    cedula      VARCHAR(20) UNIQUE NOT NULL,
    nombre      VARCHAR(150) NOT NULL,
    telefono    VARCHAR(20),
    email       VARCHAR(100),
    creado_en   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ventas (cabecera)
CREATE TABLE IF NOT EXISTS ventas (
    id              SERIAL PRIMARY KEY,
    numero_factura  VARCHAR(20) UNIQUE NOT NULL,
    cliente_id      INTEGER REFERENCES clientes(id),
    vendedor_id     INTEGER REFERENCES usuarios(id),
    fecha_hora      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal        NUMERIC(12, 2) NOT NULL DEFAULT 0,
    descuento       NUMERIC(12, 2) NOT NULL DEFAULT 0,
    total           NUMERIC(12, 2) NOT NULL DEFAULT 0,
    metodo_pago     VARCHAR(30) NOT NULL,  -- 'Efectivo', 'Transferencia'
    referencia_pago VARCHAR(100),          -- Para transferencias
    estado          VARCHAR(20) DEFAULT 'Completada',  -- 'Completada', 'Cancelada'
    notas           TEXT
);

-- Detalle de ventas
CREATE TABLE IF NOT EXISTS venta_detalles (
    id              SERIAL PRIMARY KEY,
    venta_id        INTEGER REFERENCES ventas(id) ON DELETE CASCADE,
    producto_id     INTEGER REFERENCES productos(id),
    cantidad        INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(12, 2) NOT NULL,
    subtotal        NUMERIC(12, 2) NOT NULL
);

-- ============================================================
--  Datos iniciales
-- ============================================================

INSERT INTO roles (nombre, descripcion) VALUES
    ('Gerencia',    'Acceso total al sistema'),
    ('Vendedor',    'Acceso a ventas y catálogo'),
    ('Inventario',  'Acceso a inventario y compras')
ON CONFLICT (nombre) DO NOTHING;

-- Usuario administrador por defecto  (password: admin123)
INSERT INTO usuarios (cedula, nombre, username, password_hash, rol_id)
SELECT '0000000000', 'Administrador', 'admin',
       '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMZJaaaSwm65NwQ2p0nQbWAqhO',
       r.id
FROM roles r WHERE r.nombre = 'Gerencia'
ON CONFLICT (username) DO NOTHING;

-- Categorías base
INSERT INTO categorias (nombre) VALUES
    ('Frenos'), ('Motor'), ('Suspensión'), ('Eléctrico'),
    ('Transmisión'), ('Carrocería'), ('Lubricantes'), ('Filtros')
ON CONFLICT (nombre) DO NOTHING;
