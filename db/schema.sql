-- ============================================================
--  AutoParts Express - Esquema de Base de Datos - Sprint 4
--  Acumulativo: Sprint 1 + Sprint 2 + Sprint 3 + Sprint 4
--  Nuevas tablas: auditoria, configuracion
-- ============================================================

-- Roles del sistema
CREATE TABLE IF NOT EXISTS roles (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT
);

-- Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id                SERIAL PRIMARY KEY,
    cedula            VARCHAR(20)  UNIQUE NOT NULL,
    nombre            VARCHAR(100) NOT NULL,
    username          VARCHAR(50)  UNIQUE NOT NULL,
    password_hash     VARCHAR(255) NOT NULL,
    rol_id            INTEGER REFERENCES roles(id),
    activo            BOOLEAN DEFAULT TRUE,
    intentos_fallidos INTEGER DEFAULT 0,
    bloqueado         BOOLEAN DEFAULT FALSE,
    creado_en         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sesiones
CREATE TABLE IF NOT EXISTS sesiones (
    id         SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    inicio     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fin        TIMESTAMP,
    ip         VARCHAR(45)
);

-- Categorias
CREATE TABLE IF NOT EXISTS categorias (
    id     SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL
);

-- Productos
CREATE TABLE IF NOT EXISTS productos (
    id              SERIAL PRIMARY KEY,
    codigo          VARCHAR(50)   UNIQUE NOT NULL,
    nombre          VARCHAR(150)  NOT NULL,
    descripcion     TEXT,
    categoria_id    INTEGER REFERENCES categorias(id),
    precio_unitario NUMERIC(12,2) NOT NULL CHECK (precio_unitario >= 0),
    stock_actual    INTEGER NOT NULL DEFAULT 0 CHECK (stock_actual >= 0),
    stock_minimo    INTEGER NOT NULL DEFAULT 0,
    activo          BOOLEAN DEFAULT TRUE,
    creado_en       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id        SERIAL PRIMARY KEY,
    cedula    VARCHAR(20)  UNIQUE NOT NULL,
    nombre    VARCHAR(150) NOT NULL,
    telefono  VARCHAR(20),
    email     VARCHAR(100),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ventas cabecera
CREATE TABLE IF NOT EXISTS ventas (
    id              SERIAL PRIMARY KEY,
    numero_factura  VARCHAR(20) UNIQUE NOT NULL,
    cliente_id      INTEGER REFERENCES clientes(id),
    vendedor_id     INTEGER REFERENCES usuarios(id),
    fecha_hora      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal        NUMERIC(12,2) NOT NULL DEFAULT 0,
    descuento       NUMERIC(12,2) NOT NULL DEFAULT 0,
    total           NUMERIC(12,2) NOT NULL DEFAULT 0,
    metodo_pago     VARCHAR(30) NOT NULL,
    referencia_pago VARCHAR(100),
    estado          VARCHAR(20) DEFAULT 'Completada',
    notas           TEXT
);

-- Detalle de ventas
CREATE TABLE IF NOT EXISTS venta_detalles (
    id              SERIAL PRIMARY KEY,
    venta_id        INTEGER REFERENCES ventas(id) ON DELETE CASCADE,
    producto_id     INTEGER REFERENCES productos(id),
    cantidad        INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(12,2) NOT NULL,
    descuento_item  NUMERIC(12,2) NOT NULL DEFAULT 0,
    subtotal        NUMERIC(12,2) NOT NULL
);

-- Proveedores
CREATE TABLE IF NOT EXISTS proveedores (
    id        SERIAL PRIMARY KEY,
    nombre    VARCHAR(150) NOT NULL,
    contacto  VARCHAR(100),
    telefono  VARCHAR(30),
    email     VARCHAR(100),
    nit       VARCHAR(30) UNIQUE,
    activo    BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pedidos a proveedores
CREATE TABLE IF NOT EXISTS pedidos (
    id             SERIAL PRIMARY KEY,
    numero_pedido  VARCHAR(30) UNIQUE NOT NULL,
    proveedor_id   INTEGER REFERENCES proveedores(id),
    usuario_id     INTEGER REFERENCES usuarios(id),
    fecha_pedido   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_estimada DATE NOT NULL,
    estado         VARCHAR(20) DEFAULT 'Pendiente',
    notas          TEXT
);

-- Detalle de pedidos
CREATE TABLE IF NOT EXISTS pedido_detalles (
    id          SERIAL PRIMARY KEY,
    pedido_id   INTEGER REFERENCES pedidos(id) ON DELETE CASCADE,
    producto_id INTEGER REFERENCES productos(id),
    cantidad    INTEGER NOT NULL CHECK (cantidad > 0),
    precio_ref  NUMERIC(12,2)
);

-- Alertas de stock
CREATE TABLE IF NOT EXISTS alertas_stock (
    id           SERIAL PRIMARY KEY,
    producto_id  INTEGER REFERENCES productos(id),
    stock_actual INTEGER NOT NULL,
    stock_minimo INTEGER NOT NULL,
    generada_en  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vista        BOOLEAN DEFAULT FALSE
);

-- Devoluciones Sprint 3
CREATE TABLE IF NOT EXISTS devoluciones (
    id           SERIAL PRIMARY KEY,
    numero_dev   VARCHAR(30) UNIQUE NOT NULL,
    proveedor_id INTEGER REFERENCES proveedores(id),
    producto_id  INTEGER REFERENCES productos(id),
    usuario_id   INTEGER REFERENCES usuarios(id),
    cantidad     INTEGER NOT NULL CHECK (cantidad > 0),
    motivo       TEXT NOT NULL,
    estado       VARCHAR(20) DEFAULT 'Pendiente',
    fecha        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Promociones Sprint 3
CREATE TABLE IF NOT EXISTS promociones (
    id             SERIAL PRIMARY KEY,
    nombre         VARCHAR(150)  NOT NULL,
    tipo_descuento VARCHAR(20)   NOT NULL,
    valor          NUMERIC(12,2) NOT NULL CHECK (valor > 0),
    producto_id    INTEGER REFERENCES productos(id),
    categoria_id   INTEGER REFERENCES categorias(id),
    fecha_inicio   DATE NOT NULL,
    fecha_fin      DATE NOT NULL,
    activa         BOOLEAN DEFAULT TRUE,
    creado_por     INTEGER REFERENCES usuarios(id),
    creado_en      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT promo_target CHECK (
        (producto_id IS NOT NULL AND categoria_id IS NULL) OR
        (producto_id IS NULL AND categoria_id IS NOT NULL)
    )
);

-- SPRINT 4: Auditoria de acciones del sistema
CREATE TABLE IF NOT EXISTS auditoria (
    id          SERIAL PRIMARY KEY,
    usuario_id  INTEGER REFERENCES usuarios(id),
    accion      VARCHAR(100) NOT NULL,
    modulo      VARCHAR(50)  NOT NULL,
    detalle     TEXT,
    fecha_hora  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip          VARCHAR(45)
);

-- SPRINT 4: Configuracion global del sistema
CREATE TABLE IF NOT EXISTS configuracion (
    id             SERIAL PRIMARY KEY,
    clave          VARCHAR(100) UNIQUE NOT NULL,
    valor          TEXT NOT NULL,
    descripcion    TEXT,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
--  Datos iniciales
-- ============================================================
INSERT INTO roles (nombre, descripcion) VALUES
    ('Gerencia',   'Acceso total al sistema'),
    ('Vendedor',   'Acceso a ventas y catalogo'),
    ('Inventario', 'Acceso a inventario y compras')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO usuarios (cedula, nombre, username, password_hash, rol_id)
SELECT '0000000000', 'Administrador', 'admin',
       '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMZJaaaSwm65NwQ2p0nQbWAqhO',
       r.id
FROM roles r WHERE r.nombre = 'Gerencia'
ON CONFLICT (username) DO NOTHING;

INSERT INTO categorias (nombre) VALUES
    ('Frenos'), ('Motor'), ('Suspension'), ('Electrico'),
    ('Transmision'), ('Carroceria'), ('Lubricantes'), ('Filtros')
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO proveedores (nombre, contacto, telefono, email, nit) VALUES
    ('Repuestos Colombia S.A.S', 'Carlos Mendoza', '3001234567',
     'ventas@repuestoscol.com', '900123456-1'),
    ('Moto Parts Express', 'Sandra Lopez', '3117654321',
     'pedidos@motoparts.com', '800654321-2')
ON CONFLICT (nit) DO NOTHING;

INSERT INTO configuracion (clave, valor, descripcion) VALUES
    ('empresa_nombre',    'AutoParts Express',    'Nombre de la empresa'),
    ('empresa_nit',       '900000000-0',          'NIT de la empresa'),
    ('empresa_telefono',  '3000000000',           'Telefono de contacto'),
    ('empresa_email',     'info@autoparts.com',   'Email de contacto'),
    ('empresa_direccion', 'Calle Principal #123', 'Direccion de la empresa'),
    ('moneda',            'COP',                  'Moneda del sistema'),
    ('factura_prefijo',   'FAC',                  'Prefijo para facturas'),
    ('backup_auto',       'false',                'Backup automatico activado')
ON CONFLICT (clave) DO NOTHING;
