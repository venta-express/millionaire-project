"""
AutoParts Express - Modelo de Ventas
HU-04: Registro de Venta y Emisión de Factura
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from db.connection import db_cursor


@dataclass
class ItemVenta:
    producto_id: int
    codigo: str
    nombre: str
    precio_unitario: float
    cantidad: int
    subtotal: float = field(init=False)

    def __post_init__(self):
        self.subtotal = round(self.precio_unitario * self.cantidad, 2)


@dataclass
class Cliente:
    id: int
    cedula: str
    nombre: str
    telefono: str
    email: str


# ── Clientes ─────────────────────────────────────────────────────────────────
def buscar_clientes(texto: str) -> list[Cliente]:
    like = f"%{texto.strip().lower()}%"
    with db_cursor() as cur:
        cur.execute("""
            SELECT id, cedula, nombre, telefono, email
            FROM clientes
            WHERE LOWER(nombre) LIKE %s OR cedula LIKE %s
            ORDER BY nombre LIMIT 20
        """, (like, like))
        return [Cliente(**dict(r)) for r in cur.fetchall()]


def obtener_o_crear_cliente(cedula: str, nombre: str,
                             telefono: str = "", email: str = "") -> tuple[bool, str, Optional[int]]:
    if not cedula.strip():
        return False, "La cédula es obligatoria.", None
    if not nombre.strip():
        return False, "El nombre del cliente es obligatorio.", None
    with db_cursor(commit=True) as cur:
        cur.execute("SELECT id FROM clientes WHERE cedula = %s", (cedula.strip(),))
        row = cur.fetchone()
        if row:
            return True, "Cliente encontrado.", row["id"]
        cur.execute("""
            INSERT INTO clientes (cedula, nombre, telefono, email)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (cedula.strip(), nombre.strip(), telefono, email))
        new_id = cur.fetchone()["id"]
        return True, "Cliente registrado.", new_id


def buscar_cliente_por_cedula(cedula: str) -> Optional[Cliente]:
    with db_cursor() as cur:
        cur.execute("""
            SELECT id, cedula, nombre, telefono, email
            FROM clientes WHERE cedula = %s
        """, (cedula.strip(),))
        r = cur.fetchone()
        return Cliente(**dict(r)) if r else None


# ── Número de factura ─────────────────────────────────────────────────────────
def generar_numero_factura() -> str:
    with db_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS total FROM ventas")
        n = cur.fetchone()["total"] + 1
        fecha = datetime.now().strftime("%Y%m%d")
        return f"FAC-{fecha}-{n:04d}"


# ── Registro de venta ────────────────────────────────────────────────────────
def registrar_venta(cliente_id: int, vendedor_id: int,
                    items: list[ItemVenta],
                    metodo_pago: str,
                    referencia_pago: str = "",
                    notas: str = "") -> tuple[bool, str, Optional[int]]:
    if not items:
        return False, "La venta debe tener al menos un producto.", None
    if metodo_pago not in ("Efectivo", "Transferencia"):
        return False, "Método de pago inválido.", None
    if metodo_pago == "Transferencia" and not referencia_pago.strip():
        return False, "Ingresa la referencia de la transferencia.", None

    subtotal = round(sum(i.subtotal for i in items), 2)
    total = subtotal
    numero = generar_numero_factura()

    try:
        with db_cursor(commit=True) as cur:
            # Verificar stock antes de proceder
            for item in items:
                cur.execute("SELECT stock_actual, nombre FROM productos WHERE id=%s FOR UPDATE",
                            (item.producto_id,))
                row = cur.fetchone()
                if not row:
                    raise ValueError(f"Producto ID {item.producto_id} no encontrado.")
                if row["stock_actual"] < item.cantidad:
                    raise ValueError(
                        f"Stock insuficiente para '{row['nombre']}'. "
                        f"Disponible: {row['stock_actual']}, solicitado: {item.cantidad}."
                    )

            # Insertar venta
            cur.execute("""
                INSERT INTO ventas
                    (numero_factura, cliente_id, vendedor_id, subtotal,
                     descuento, total, metodo_pago, referencia_pago, notas)
                VALUES (%s, %s, %s, %s, 0, %s, %s, %s, %s)
                RETURNING id
            """, (numero, cliente_id, vendedor_id, subtotal, total,
                  metodo_pago, referencia_pago, notas))
            venta_id = cur.fetchone()["id"]

            # Insertar detalles y actualizar stock
            for item in items:
                cur.execute("""
                    INSERT INTO venta_detalles
                        (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, (venta_id, item.producto_id, item.cantidad,
                      item.precio_unitario, item.subtotal))
                cur.execute("""
                    UPDATE productos
                    SET stock_actual = stock_actual - %s, actualizado_en = NOW()
                    WHERE id = %s
                """, (item.cantidad, item.producto_id))

        return True, numero, venta_id
    except ValueError as e:
        return False, str(e), None
    except Exception as e:
        return False, f"Error al registrar venta: {e}", None


# ── Consulta de venta ─────────────────────────────────────────────────────────
def obtener_venta(venta_id: int) -> Optional[dict]:
    with db_cursor() as cur:
        cur.execute("""
            SELECT v.*, c.nombre AS cliente_nombre, c.cedula AS cliente_cedula,
                   u.nombre AS vendedor_nombre
            FROM ventas v
            JOIN clientes c ON c.id = v.cliente_id
            JOIN usuarios u ON u.id = v.vendedor_id
            WHERE v.id = %s
        """, (venta_id,))
        venta = dict(cur.fetchone())

        cur.execute("""
            SELECT d.cantidad, d.precio_unitario, d.subtotal,
                   p.codigo, p.nombre
            FROM venta_detalles d
            JOIN productos p ON p.id = d.producto_id
            WHERE d.venta_id = %s
        """, (venta_id,))
        venta["detalles"] = [dict(r) for r in cur.fetchall()]
        return venta
