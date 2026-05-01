"""
AutoParts Express - Modelo de Ventas
HU-01: Registro de Venta y Emisión de Factura (Sprint 1)
HU-07: Historial de Compras de Clientes       (Sprint 2 - nuevo)

Sprint 2: después de registrar una venta se dispara la verificación
de alertas de stock mínimo para cada producto vendido.
"""

# dataclass + field para el cálculo automático del subtotal
from dataclasses import dataclass, field

# Optional para valores que pueden ser None
from typing import Optional

# datetime para generar el número de factura con la fecha actual
from datetime import datetime

# Context manager de conexión a PostgreSQL
from db.connection import db_cursor

# Importamos la función de alerta del modelo de inventario (Sprint 2)
from models.inventario import _registrar_alerta_si_necesario


# ── Dataclass ItemVenta ───────────────────────────────────────────────────────
@dataclass
class ItemVenta:
    """Representa una línea de producto dentro de una venta."""
    producto_id:     int    # FK a la tabla productos
    codigo:          str    # Código del producto (para mostrar en factura)
    nombre:          str    # Nombre del producto (para mostrar en factura)
    precio_unitario: float  # Precio al momento de la venta (puede diferir del actual)
    cantidad:        int    # Unidades vendidas

    # subtotal se calcula automáticamente; no se pasa en el constructor
    subtotal: float = field(init=False)

    def __post_init__(self):
        """Se ejecuta automáticamente después de __init__ para calcular el subtotal."""
        self.subtotal = round(self.precio_unitario * self.cantidad, 2)


# ── Dataclass Cliente ─────────────────────────────────────────────────────────
@dataclass
class Cliente:
    """Representa un cliente registrado en el sistema."""
    id:       int   # PK de la tabla clientes
    cedula:   str   # Documento de identidad único
    nombre:   str   # Nombre completo
    telefono: str   # Número de contacto
    email:    str   # Correo electrónico


# ── Clientes ───────────────────────────────────────────────────────────────────

def buscar_clientes(texto: str) -> list[Cliente]:
    """
    Busca clientes por nombre o cédula con búsqueda parcial (LIKE).
    Retorna hasta 20 resultados ordenados alfabéticamente.
    """
    # Construimos el patrón de búsqueda en minúsculas para case-insensitive
    like = f"%{texto.strip().lower()}%"

    with db_cursor() as cur:
        cur.execute("""
            SELECT id, cedula, nombre, telefono, email
            FROM clientes
            WHERE LOWER(nombre) LIKE %s OR cedula LIKE %s
            ORDER BY nombre LIMIT 20  -- Limitamos a 20 para rendimiento
        """, (like, like))
        return [Cliente(**dict(r)) for r in cur.fetchall()]


def obtener_o_crear_cliente(cedula: str, nombre: str,
                             telefono: str = "", email: str = "") -> tuple[bool, str, Optional[int]]:
    """
    Busca un cliente por cédula y lo retorna si existe, o lo crea si no.
    Retorna (exito: bool, mensaje: str, cliente_id | None).
    Garantiza que no haya duplicados por cédula.
    """
    # Validaciones de campos obligatorios
    if not cedula.strip():
        return False, "La cédula es obligatoria.", None
    if not nombre.strip():
        return False, "El nombre del cliente es obligatorio.", None

    with db_cursor(commit=True) as cur:
        # Primero buscamos si ya existe el cliente con esa cédula
        cur.execute("SELECT id FROM clientes WHERE cedula = %s", (cedula.strip(),))
        row = cur.fetchone()

        if row:
            # El cliente ya existe; retornamos su ID sin crear duplicado
            return True, "Cliente encontrado.", row["id"]

        # No existe: lo creamos con los datos proporcionados
        cur.execute("""
            INSERT INTO clientes (cedula, nombre, telefono, email)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (cedula.strip(), nombre.strip(), telefono, email))
        new_id = cur.fetchone()["id"]
        return True, "Cliente registrado.", new_id


def buscar_cliente_por_cedula(cedula: str) -> Optional[Cliente]:
    """
    Retorna un cliente exacto por su cédula, o None si no existe.
    Usado para autocompletar el formulario de venta.
    """
    with db_cursor() as cur:
        cur.execute("""
            SELECT id, cedula, nombre, telefono, email
            FROM clientes WHERE cedula = %s
        """, (cedula.strip(),))
        r = cur.fetchone()
        return Cliente(**dict(r)) if r else None


# ── Número de factura ──────────────────────────────────────────────────────────
def generar_numero_factura() -> str:
    """
    Genera un número de factura único con formato FAC-YYYYMMDD-NNNN.
    El número correlativo se basa en el total de ventas existentes.
    """
    with db_cursor() as cur:
        # Contamos las ventas para el correlativo (n+1 garantiza unicidad básica)
        cur.execute("SELECT COUNT(*) AS total FROM ventas")
        n = cur.fetchone()["total"] + 1

    # Fecha actual en formato compacto (sin separadores)
    fecha = datetime.now().strftime("%Y%m%d")

    # Número de 4 dígitos con cero-relleno: 0001, 0002...
    return f"FAC-{fecha}-{n:04d}"


# ── Registro de venta (HU-01 Sprint 1 + alerta Sprint 2) ─────────────────────
def registrar_venta(cliente_id: int, vendedor_id: int,
                    items: list[ItemVenta],
                    metodo_pago: str,
                    referencia_pago: str = "",
                    notas: str = "") -> tuple[bool, str, Optional[int]]:
    """
    Registra una venta completa en la BD de forma atómica:
      1. Verifica stock disponible para todos los ítems.
      2. Inserta la cabecera de venta.
      3. Inserta los detalles de venta.
      4. Descuenta el stock de cada producto.
      5. (Sprint 2) Verifica y registra alertas de stock mínimo.
    Retorna (exito: bool, numero_factura | mensaje_error: str, venta_id | None).
    """
    # Validación: la venta debe tener al menos un ítem
    if not items:
        return False, "La venta debe tener al menos un producto.", None

    # Validación: método de pago debe ser uno de los valores permitidos
    if metodo_pago not in ("Efectivo", "Transferencia"):
        return False, "Método de pago inválido.", None

    # Si el pago es transferencia, la referencia es obligatoria
    if metodo_pago == "Transferencia" and not referencia_pago.strip():
        return False, "Ingresa la referencia de la transferencia.", None

    # Calculamos el subtotal sumando los subtotales de cada ítem
    subtotal = round(sum(i.subtotal for i in items), 2)
    total = subtotal  # En Sprint 1 no hay descuentos globales adicionales

    # Generamos el número de factura antes de abrir la transacción
    numero = generar_numero_factura()

    # Lista para guardar los IDs de productos afectados (para alertas post-venta)
    productos_afectados = []

    try:
        with db_cursor(commit=True) as cur:
            # ── 1. Verificar stock con bloqueo de filas (FOR UPDATE) ──────────
            for item in items:
                # FOR UPDATE bloquea la fila para evitar condiciones de carrera
                cur.execute(
                    "SELECT stock_actual, nombre FROM productos WHERE id=%s FOR UPDATE",
                    (item.producto_id,)
                )
                row = cur.fetchone()

                # El producto debe existir en la BD
                if not row:
                    raise ValueError(f"Producto ID {item.producto_id} no encontrado.")

                # El stock debe ser suficiente para satisfacer la cantidad pedida
                if row["stock_actual"] < item.cantidad:
                    raise ValueError(
                        f"Stock insuficiente para '{row['nombre']}'. "
                        f"Disponible: {row['stock_actual']}, solicitado: {item.cantidad}."
                    )

            # ── 2. Insertar cabecera de venta ─────────────────────────────────
            cur.execute("""
                INSERT INTO ventas
                    (numero_factura, cliente_id, vendedor_id, subtotal,
                     descuento, total, metodo_pago, referencia_pago, notas)
                VALUES (%s, %s, %s, %s, 0, %s, %s, %s, %s)
                RETURNING id  -- Necesitamos el ID para insertar los detalles
            """, (numero, cliente_id, vendedor_id, subtotal, total,
                  metodo_pago, referencia_pago, notas))
            venta_id = cur.fetchone()["id"]

            # ── 3 & 4. Insertar detalles y descontar stock ────────────────────
            for item in items:
                # Insertamos el ítem de detalle de venta
                cur.execute("""
                    INSERT INTO venta_detalles
                        (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, (venta_id, item.producto_id, item.cantidad,
                      item.precio_unitario, item.subtotal))

                # Descontamos la cantidad vendida del stock actual
                cur.execute("""
                    UPDATE productos
                    SET stock_actual = stock_actual - %s, actualizado_en = NOW()
                    WHERE id = %s
                """, (item.cantidad, item.producto_id))

                # Guardamos el ID del producto para verificar alertas después
                productos_afectados.append(item.producto_id)

        # ── 5. Sprint 2: verificar alertas FUERA de la transacción principal ──
        # Lo hacemos fuera del with para que la venta ya esté confirmada
        for pid in productos_afectados:
            _registrar_alerta_si_necesario(pid)

        return True, numero, venta_id

    except ValueError as e:
        # Error de negocio (stock insuficiente, producto no encontrado)
        return False, str(e), None

    except Exception as e:
        # Error de BD u otro error inesperado
        return False, f"Error al registrar venta: {e}", None


# ── Consulta de venta ──────────────────────────────────────────────────────────
def obtener_venta(venta_id: int) -> Optional[dict]:
    """
    Retorna los datos completos de una venta: cabecera + detalles.
    Incluye nombre del cliente, cédula y nombre del vendedor (via JOIN).
    Retorna None si la venta no existe.
    """
    with db_cursor() as cur:
        # Cabecera con datos de cliente y vendedor
        cur.execute("""
            SELECT v.*, c.nombre AS cliente_nombre, c.cedula AS cliente_cedula,
                   u.nombre AS vendedor_nombre
            FROM ventas v
            JOIN clientes c ON c.id = v.cliente_id
            JOIN usuarios u ON u.id = v.vendedor_id
            WHERE v.id = %s
        """, (venta_id,))
        venta = dict(cur.fetchone())  # Convertimos a dict mutable

        # Ítems del detalle con código y nombre del producto
        cur.execute("""
            SELECT d.cantidad, d.precio_unitario, d.subtotal,
                   p.codigo, p.nombre
            FROM venta_detalles d
            JOIN productos p ON p.id = d.producto_id
            WHERE d.venta_id = %s
        """, (venta_id,))
        venta["detalles"] = [dict(r) for r in cur.fetchall()]

    return venta


# ── Historial de compras de clientes (HU-07 - Sprint 2) ──────────────────────

def historial_cliente(cliente_id: int) -> list[dict]:
    """
    Retorna todas las facturas de un cliente con sus detalles.
    Cada elemento es un dict con la cabecera de venta y una lista 'detalles'.
    Usado en el módulo de Clientes para consultas de historial.
    """
    with db_cursor() as cur:
        # Traemos las ventas del cliente ordenadas de más reciente a más antigua
        cur.execute("""
            SELECT v.id, v.numero_factura, v.fecha_hora,
                   v.total, v.metodo_pago, v.estado,
                   u.nombre AS vendedor_nombre
            FROM ventas v
            JOIN usuarios u ON u.id = v.vendedor_id
            WHERE v.cliente_id = %s
            ORDER BY v.fecha_hora DESC  -- Más recientes primero
        """, (cliente_id,))
        ventas = [dict(r) for r in cur.fetchall()]

        # Para cada venta, cargamos sus ítems de detalle
        for v in ventas:
            cur.execute("""
                SELECT d.cantidad, d.precio_unitario, d.subtotal,
                       p.codigo, p.nombre
                FROM venta_detalles d
                JOIN productos p ON p.id = d.producto_id
                WHERE d.venta_id = %s
            """, (v["id"],))
            v["detalles"] = [dict(r) for r in cur.fetchall()]

    return ventas  # Lista de dicts con cabecera + detalles anidados


def buscar_clientes_historial(texto: str) -> list[dict]:
    """
    Busca clientes por nombre o cédula para el módulo de historial.
    Retorna dicts con datos del cliente más el total de compras y número de facturas.
    """
    like = f"%{texto.strip().lower()}%"  # Patrón de búsqueda parcial case-insensitive

    with db_cursor() as cur:
        cur.execute("""
            SELECT c.id, c.cedula, c.nombre, c.telefono, c.email,
                   -- Contamos las facturas y sumamos el total comprado (subquery agregada)
                   COUNT(v.id)     AS total_facturas,
                   COALESCE(SUM(v.total), 0) AS total_comprado
            FROM clientes c
            LEFT JOIN ventas v ON v.cliente_id = c.id  -- LEFT JOIN para incluir clientes sin ventas
            WHERE LOWER(c.nombre) LIKE %s OR c.cedula LIKE %s
            GROUP BY c.id, c.cedula, c.nombre, c.telefono, c.email
            ORDER BY c.nombre
            LIMIT 50  -- Limitamos el resultado para no saturar la UI
        """, (like, like))
        return [dict(r) for r in cur.fetchall()]
