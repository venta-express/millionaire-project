-- ============================================================
--  AutoParts Express - Esquema de Base de Datos - Sprint 2
--  Módulo: Seguridad + Inventario + Ventas (Sprint 1)
--           + Proveedores + Pedidos + Alertas Stock (Sprint 2)
-- ============================================================

-- ── Roles del sistema ─────────────────────────────────────────────────────────
-- Almacena los tres roles posibles: Gerencia, Vendedor, Inventario
CREATE TABLE IF NOT EXISTS roles (
    id          SERIAL PRIMARY KEY,           -- Identificador auto-incremental
    nombre      VARCHAR(50) UNIQUE NOT NULL,  -- Nombre único del rol
    descripcion TEXT                          -- Descripción opcional del rol
);

-- ── Usuarios del sistema ──────────────────────────────────────────────────────
-- Un usuario pertenece a un rol y puede iniciar sesión con username+password
CREATE TABLE IF NOT EXISTS usuarios (
    id                SERIAL PRIMARY KEY,
    cedula            VARCHAR(20)  UNIQUE NOT NULL,   -- Documento de identidad único
    nombre            VARCHAR(100) NOT NULL,           -- Nombre completo
    username          VARCHAR(50)  UNIQUE NOT NULL,    -- Nombre de usuario para login
    password_hash     VARCHAR(255) NOT NULL,           -- Hash bcrypt de la contraseña
    rol_id            INTEGER REFERENCES roles(id),    -- FK al rol asignado
    activo            BOOLEAN DEFAULT TRUE,            -- FALSE = cuenta desactivada
    intentos_fallidos INTEGER DEFAULT 0,              -- Contador de fallos de login
    bloqueado         BOOLEAN DEFAULT FALSE,           -- TRUE = cuenta bloqueada
    creado_en         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Sesiones activas (auditoría) ─────────────────────────────────────────────
-- Registra cada inicio de sesión para trazabilidad
CREATE TABLE IF NOT EXISTS sesiones (
    id          SERIAL PRIMARY KEY,
    usuario_id  INTEGER REFERENCES usuarios(id),  -- Quién inició sesión
    inicio      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fin         TIMESTAMP,                         -- NULL mientras la sesión está activa
    ip          VARCHAR(45)                        -- Dirección IP del cliente
);

-- ── Categorías de productos ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS categorias (
    id      SERIAL PRIMARY KEY,
    nombre  VARCHAR(100) UNIQUE NOT NULL
);

-- ── Productos / Inventario ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS productos (
    id              SERIAL PRIMARY KEY,
    codigo          VARCHAR(50)  UNIQUE NOT NULL,              -- Código único de referencia
    nombre          VARCHAR(150) NOT NULL,
    descripcion     TEXT,
    categoria_id    INTEGER REFERENCES categorias(id),
    precio_unitario NUMERIC(12, 2) NOT NULL CHECK (precio_unitario >= 0),
    stock_actual    INTEGER NOT NULL DEFAULT 0 CHECK (stock_actual >= 0),
    stock_minimo    INTEGER NOT NULL DEFAULT 0,               -- Umbral para alertas
    activo          BOOLEAN DEFAULT TRUE,
    creado_en       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Clientes ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS clientes (
    id          SERIAL PRIMARY KEY,
    cedula      VARCHAR(20)  UNIQUE NOT NULL,
    nombre      VARCHAR(150) NOT NULL,
    telefono    VARCHAR(20),
    email       VARCHAR(100),
    creado_en   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Ventas (cabecera) ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ventas (
    id              SERIAL PRIMARY KEY,
    numero_factura  VARCHAR(20) UNIQUE NOT NULL,
    cliente_id      INTEGER REFERENCES clientes(id),
    vendedor_id     INTEGER REFERENCES usuarios(id),
    fecha_hora      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal        NUMERIC(12, 2) NOT NULL DEFAULT 0,
    descuento       NUMERIC(12, 2) NOT NULL DEFAULT 0,
    total           NUMERIC(12, 2) NOT NULL DEFAULT 0,
    metodo_pago     VARCHAR(30) NOT NULL,      -- 'Efectivo' | 'Transferencia'
    referencia_pago VARCHAR(100),              -- Requerido si es transferencia
    estado          VARCHAR(20) DEFAULT 'Completada',  -- 'Completada' | 'Cancelada'
    notas           TEXT
);

-- ── Detalle de ventas ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS venta_detalles (
    id              SERIAL PRIMARY KEY,
    venta_id        INTEGER REFERENCES ventas(id) ON DELETE CASCADE,
    producto_id     INTEGER REFERENCES productos(id),
    cantidad        INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(12, 2) NOT NULL,
    subtotal        NUMERIC(12, 2) NOT NULL
);

-- ── SPRINT 2: Proveedores ─────────────────────────────────────────────────────
-- Empresas o personas que suministran productos al negocio
CREATE TABLE IF NOT EXISTS proveedores (
    id        SERIAL PRIMARY KEY,
    nombre    VARCHAR(150) NOT NULL,           -- Razón social o nombre comercial
    contacto  VARCHAR(100),                    -- Nombre de la persona de contacto
    telefono  VARCHAR(30),
    email     VARCHAR(100),
    nit       VARCHAR(30) UNIQUE,              -- NIT o RUT del proveedor
    activo    BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── SPRINT 2: Pedidos a proveedores ──────────────────────────────────────────
-- Cabecera del pedido (orden de compra)
CREATE TABLE IF NOT EXISTS pedidos (
    id               SERIAL PRIMARY KEY,
    numero_pedido    VARCHAR(30) UNIQUE NOT NULL,  -- Número generado automáticamente
    proveedor_id     INTEGER REFERENCES proveedores(id),
    usuario_id       INTEGER REFERENCES usuarios(id), -- Quién generó el pedido
    fecha_pedido     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_estimada   DATE NOT NULL,                -- Fecha comprometida de entrega
    estado           VARCHAR(20) DEFAULT 'Pendiente',
    -- Estados posibles: 'Pendiente' | 'Recibido' | 'Cancelado'
    notas            TEXT
);

-- ── SPRINT 2: Detalle de pedidos ─────────────────────────────────────────────
-- Ítems que componen cada pedido a proveedor
CREATE TABLE IF NOT EXISTS pedido_detalles (
    id          SERIAL PRIMARY KEY,
    pedido_id   INTEGER REFERENCES pedidos(id) ON DELETE CASCADE,
    producto_id INTEGER REFERENCES productos(id),
    cantidad    INTEGER NOT NULL CHECK (cantidad > 0),  -- Unidades solicitadas
    precio_ref  NUMERIC(12, 2)                          -- Precio de referencia (opcional)
);

-- ── SPRINT 2: Historial de alertas de stock ───────────────────────────────────
-- Registra cada vez que un producto cayó por debajo del stock mínimo
CREATE TABLE IF NOT EXISTS alertas_stock (
    id           SERIAL PRIMARY KEY,
    producto_id  INTEGER REFERENCES productos(id),
    stock_actual INTEGER NOT NULL,   -- Stock al momento de generar la alerta
    stock_minimo INTEGER NOT NULL,   -- Mínimo configurado en ese momento
    generada_en  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vista        BOOLEAN DEFAULT FALSE  -- TRUE cuando el usuario la reconoció
);

-- ============================================================
--  Datos iniciales (idempotentes con ON CONFLICT DO NOTHING)
-- ============================================================

-- Roles base del sistema
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

-- Categorías base de productos
INSERT INTO categorias (nombre) VALUES
    ('Frenos'), ('Motor'), ('Suspensión'), ('Eléctrico'),
    ('Transmisión'), ('Carrocería'), ('Lubricantes'), ('Filtros')
ON CONFLICT (nombre) DO NOTHING;

-- Proveedor de ejemplo para pruebas del Sprint 2
INSERT INTO proveedores (nombre, contacto, telefono, email, nit) VALUES
    ('Repuestos Colombia S.A.S', 'Carlos Mendoza', '3001234567', 'ventas@repuestoscol.com', '900123456-1'),
    ('Moto Parts Express', 'Sandra López',   '3117654321', 'pedidos@motoparts.com',    '800654321-2')
ON CONFLICT (nit) DO NOTHING;
