# AutoParts Express — Sprint 2

## Módulos incluidos

| Sprint | HU | Módulo | Descripción |
|--------|----|--------|-------------|
| 1 | HU-01 | Seguridad | Inicio de sesión con roles y bloqueo por intentos |
| 1 | HU-02 | Inventario | Registro y gestión de productos |
| 1 | HU-03 | Inventario | Búsqueda y filtrado en tiempo real |
| 1 | HU-04 | Ventas | Registro de ventas y emisión de facturas |
| **2** | **HU-05** | **Inventario** | **Alertas automáticas de stock mínimo** |
| **2** | **HU-06** | **Compras** | **Gestión de pedidos a proveedores** |
| **2** | **HU-07** | **Clientes** | **Historial de compras por cliente** |
| **2** | **HU-08** | **Usuarios** | **Gestión de usuarios y roles (solo Gerencia)** |

## Estructura de carpetas

```
autoparts/
├── main.py                  # Punto de entrada
├── requirements.txt
├── db/
│   ├── connection.py        # Gestor de conexión PostgreSQL
│   └── schema.sql           # Esquema completo Sprint 1 + Sprint 2
├── models/
│   ├── auth.py              # Autenticación + CRUD usuarios (HU-08)
│   ├── inventario.py        # CRUD productos + alertas stock (HU-05)
│   ├── ventas.py            # Ventas + historial clientes (HU-07)
│   └── compras.py           # Proveedores + pedidos (HU-06)  ← NUEVO
├── ui/
│   ├── login.py             # Pantalla de login
│   ├── main_window.py       # Ventana principal + sidebar con roles
│   ├── inventario.py        # Vista de inventario
│   ├── ventas.py            # Vista de ventas
│   ├── clientes.py          # Vista de clientes ← NUEVO
│   ├── compras.py           # Vista de compras  ← NUEVO
│   └── usuarios.py          # Vista de usuarios ← NUEVO
└── utils/
    └── styles.py            # Estilos y paleta de colores
```

## Configuración

### 1. Base de datos

Edita `db/connection.py` con tus credenciales de PostgreSQL:

```python
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "autoparts_db",
    "user":     "postgres",
    "password": "TU_CONTRASEÑA",
}
```

### 2. Inicializar el esquema

Ejecuta el SQL en pgAdmin o psql para crear las tablas nuevas del Sprint 2
(proveedores, pedidos, pedido_detalles, alertas_stock):

```bash
psql -U postgres -d autoparts_db -f db/schema.sql
```

O desde Python:

```python
from db.connection import init_db
init_db()
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar

```bash
cd autoparts/
python main.py
```

## Credenciales por defecto

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | admin123 | Gerencia |

## Permisos por rol

| Módulo | Gerencia | Vendedor | Inventario |
|--------|----------|----------|------------|
| Inicio | ✅ | ✅ | ✅ |
| Inventario | ✅ | ❌ | ✅ |
| Ventas | ✅ | ✅ | ❌ |
| Clientes | ✅ | ✅ | ❌ |
| Compras | ✅ | ❌ | ✅ |
| Usuarios | ✅ | ❌ | ❌ |
