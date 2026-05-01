"""
AutoParts Express - Modelo de Devoluciones a Proveedores
HU-11: Devoluciones a Proveedores (Sprint 3)

Responsabilidades:
  - Registrar devoluciones de productos defectuosos o incorrectos
  - Descontar el stock del producto al crear la devolución
  - Cambiar el estado de una devolución (Pendiente → Procesada / Rechazada)
  - Listar devoluciones con filtros
"""

from dataclasses import dataclass        # Para la clase Devolucion
from typing import Optional              # Para valores que pueden ser None
from datetime import datetime            # Para la fecha de registro
from db.connection import db_cursor     # Context manager de BD


# ── Dataclass Devolucion ──────────────────────────────────────────────────────
@dataclass
class Devolucion:
    """Representa una devolución de producto a proveedor."""
    id:               int       # PK de la tabla devoluciones
    numero_dev:       str       # Número de devolución (DEV-YYYYMMDD-NNNN)
    proveedor_id:     int       # FK al proveedor
    proveedor_nombre: str       # Nombre del proveedor (via JOIN)
    producto_id:      int       # FK al producto devuelto
    producto_nombre:  str       # Nombre del producto (via JOIN)
    producto_codigo:  str       # Código del producto (via JOIN)
    usuario_id:       int       # FK al usuario que registró la devolución
    usuario_nombre:   str       # Nombre del usuario (via JOIN)
    cantidad:         int       # Unidades devueltas
    motivo:           str       # Razón de la devolución
    estado:           str       # 'Pendiente' | 'Procesada' | 'Rechazada'
    fecha:            datetime  # Fecha y hora de registro


# ── Generador de número de devolución ─────────────────────────────────────────
def _generar_numero_dev() -> str:
    """
    Genera un número único para la devolución: DEV-YYYYMMDD-NNNN.
    Función privada usada internamente por registrar_devolucion.
    """
    with db_cursor() as cur:
        # Contamos las devoluciones existentes para el correlativo
        cur.execute("SELECT COUNT(*) AS total FROM devoluciones")
        n = cur.fetchone()["total"] + 1

    # Fecha compacta sin separadores para el código
    fecha = datetime.now().strftime("%Y%m%d")
    return f"DEV-{fecha}-{n:04d}"


# ── Registro de devolución (HU-11) ────────────────────────────────────────────
def registrar_devolucion(proveedor_id: int, producto_id: int,
                          usuario_id: int, cantidad: int,
                          motivo: str) -> tuple[bool, str, Optional[int]]:
    """
    Registra una nueva devolución a proveedor y descuenta el stock del producto.
    El estado inicial siempre es 'Pendiente'.

    Parámetros:
        proveedor_id: ID del proveedor al que se devuelve
        producto_id:  ID del producto devuelto
        usuario_id:   ID del usuario que registra la devolución
        cantidad:     Unidades a devolver
        motivo:       Descripción del motivo (defecto, error de pedido, etc.)

    Retorna: (exito: bool, numero_dev | mensaje_error: str, devolucion_id | None)
    """
    # Validaciones básicas antes de tocar la BD
    if cantidad <= 0:
        return False, "La cantidad debe ser mayor a cero.", None

    if not motivo.strip():
        return False, "Debe ingresar el motivo de la devolución.", None

    # Generamos el número de devolución antes de abrir la transacción
    numero = _generar_numero_dev()

    try:
        with db_cursor(commit=True) as cur:
            # Verificamos que el producto tenga suficiente stock para descontar
            cur.execute(
                "SELECT stock_actual, nombre FROM productos WHERE id=%s FOR UPDATE",
                (producto_id,)
            )
            prod = cur.fetchone()
            if not prod:
                return False, "Producto no encontrado.", None

            if prod["stock_actual"] < cantidad:
                return False, (
                    f"Stock insuficiente para devolver. "
                    f"Disponible: {prod['stock_actual']}, solicitado: {cantidad}."
                ), None

            # Insertamos el registro de devolución con estado inicial 'Pendiente'
            cur.execute("""
                INSERT INTO devoluciones
                    (numero_dev, proveedor_id, producto_id, usuario_id, cantidad, motivo)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (numero, proveedor_id, producto_id, usuario_id, cantidad, motivo.strip()))
            dev_id = cur.fetchone()["id"]

            # Descontamos el stock del producto devuelto
            cur.execute("""
                UPDATE productos
                SET stock_actual = stock_actual - %s, actualizado_en = NOW()
                WHERE id = %s
            """, (cantidad, producto_id))

        return True, numero, dev_id

    except Exception as e:
        return False, f"Error al registrar devolución: {e}", None


# ── Listado de devoluciones ───────────────────────────────────────────────────
def listar_devoluciones(estado: Optional[str] = None,
                         proveedor_id: Optional[int] = None) -> list[Devolucion]:
    """
    Retorna devoluciones con datos del proveedor, producto y usuario.
    Parámetros opcionales de filtro:
        estado:       'Pendiente' | 'Procesada' | 'Rechazada' | None (todos)
        proveedor_id: filtra por proveedor específico
    """
    # Construimos la cláusula WHERE dinámicamente
    conditions = []
    params = []

    if estado:
        conditions.append("d.estado = %s")
        params.append(estado)

    if proveedor_id:
        conditions.append("d.proveedor_id = %s")
        params.append(proveedor_id)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    with db_cursor() as cur:
        cur.execute(f"""
            SELECT d.id, d.numero_dev, d.proveedor_id,
                   prov.nombre  AS proveedor_nombre,
                   d.producto_id,
                   prod.nombre  AS producto_nombre,
                   prod.codigo  AS producto_codigo,
                   d.usuario_id,
                   u.nombre     AS usuario_nombre,
                   d.cantidad, d.motivo, d.estado, d.fecha
            FROM devoluciones d
            JOIN proveedores prov ON prov.id = d.proveedor_id
            JOIN productos   prod ON prod.id = d.producto_id
            JOIN usuarios    u    ON u.id    = d.usuario_id
            {where}
            ORDER BY d.fecha DESC   -- Las más recientes primero
        """, params)
        return [Devolucion(**dict(r)) for r in cur.fetchall()]


def actualizar_estado_devolucion(dev_id: int, nuevo_estado: str) -> tuple[bool, str]:
    """
    Cambia el estado de una devolución.
    Si el estado pasa a 'Rechazada', el stock del producto se restaura
    (se devuelven las unidades al inventario).
    """
    estados_validos = ("Pendiente", "Procesada", "Rechazada")
    if nuevo_estado not in estados_validos:
        return False, f"Estado inválido. Opciones: {', '.join(estados_validos)}."

    with db_cursor(commit=True) as cur:
        # Obtenemos los datos de la devolución para posible restauración de stock
        cur.execute(
            "SELECT producto_id, cantidad, estado FROM devoluciones WHERE id=%s",
            (dev_id,)
        )
        dev = cur.fetchone()
        if not dev:
            return False, "Devolución no encontrada."

        # Si la devolución es rechazada y estaba pendiente, restauramos el stock
        if nuevo_estado == "Rechazada" and dev["estado"] == "Pendiente":
            cur.execute("""
                UPDATE productos
                SET stock_actual = stock_actual + %s, actualizado_en = NOW()
                WHERE id = %s
            """, (dev["cantidad"], dev["producto_id"]))

        # Actualizamos el estado en la tabla devoluciones
        cur.execute("UPDATE devoluciones SET estado=%s WHERE id=%s", (nuevo_estado, dev_id))

    return True, f"Devolución marcada como '{nuevo_estado}'."
