# AutoParts Express — Sistema de Gestión
## Sprint 1: Seguridad + Inventario + Ventas

### Tecnologías
- **Frontend**: PySide6 (Qt6)
- **Backend lógica**: Python 3.11+
- **Base de datos**: PostgreSQL

---

## Estructura del Proyecto

```
autoparts/
├── main.py                  # Punto de entrada
├── requirements.txt
├── db/
│   ├── connection.py        # Conexión PostgreSQL
│   └── schema.sql           # Tablas + datos base
├── models/
│   ├── auth.py              # HU-01: Login / sesión / usuarios
│   ├── inventario.py        # HU-02 + HU-03: Productos
│   └── ventas.py            # HU-04: Ventas / facturas / clientes
├── ui/
│   ├── login.py             # HU-01: Pantalla de login
│   ├── inventario.py        # HU-02 + HU-03: Vista de inventario
│   ├── ventas.py            # HU-04: Vista de ventas
│   └── main_window.py       # Ventana principal + sidebar
└── utils/
    └── styles.py            # Estilos globales (paleta + QSS)
```

---

## Configuración e Instalación

### 1. Instalar dependencias Python
```bash
pip install -r requirements.txt
```

### 2. Crear la base de datos en PostgreSQL
```sql
CREATE DATABASE autoparts_db;
```

### 3. Configurar credenciales de BD
Edita `db/connection.py` y ajusta:
```python
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "autoparts_db",
    "user":     "postgres",
    "password": "TU_CONTRASEÑA",
}
```

### 4. Inicializar el esquema
```bash
cd autoparts
python -c "from db.connection import init_db; init_db()"
```

### 5. Ejecutar la aplicación
```bash
python main.py
```

---

## Credenciales por defecto

| Campo    | Valor      |
|----------|------------|
| Usuario  | `admin`    |
| Contraseña | `admin123` |
| Rol      | Gerencia   |

---

## Historias de Usuario — Sprint 1

### HU-01 · Inicio de Sesión ✅
- Pantalla dividida: panel de marca (izq) + formulario (der)
- Validación de credenciales con bcrypt
- Bloqueo automático tras 3 intentos fallidos
- Redirección según rol del usuario
- Animación de sacudida en credenciales incorrectas

### HU-02 · Registro de Productos ✅
- Formulario completo: código, nombre, categoría, precio, stock inicial, stock mínimo
- Validación de duplicados por código
- Alertas visuales de stock bajo directamente en la tabla

### HU-03 · Búsqueda y Filtrado ✅
- Búsqueda en tiempo real (debounce 300 ms → garantiza < 2 seg)
- Filtro por nombre, código y categoría simultáneamente
- Badges de estado: OK / Stock bajo / Sin stock
- Acciones de editar y eliminar por fila

### HU-04 · Registro de Venta y Emisión de Factura ✅
- Panel de dos columnas: catálogo de productos + carrito
- Agregar/quitar ítems, ajustar cantidades
- Validación de stock en tiempo real
- Registro del cliente (buscar por cédula o crear nuevo)
- Métodos de pago: Efectivo / Transferencia (con referencia)
- Factura generada con: número, fecha, vendedor, cliente, ítems, subtotales, total
- Descuento de stock automático al confirmar venta

---

## Próximos Sprints

| Sprint | Módulos |
|--------|---------|
| Sprint 2 | Alertas stock mínimo, Pedidos a proveedores, Historial clientes, Gestión usuarios/roles |
| Sprint 3 | Reportes exportables (PDF/Excel), Devoluciones, Promociones |
| Sprint 4 | Integración, pruebas, ajustes finales |
