"""
AutoParts Express - Modelo de Compras y Proveedores
HU-06: Gestión de Pedidos a Proveedores (Sprint 2 - nuevo)

Responsabilidades:
  - CRUD de proveedores
  - Registro y seguimiento de pedidos a proveedores
  - Consulta de pedidos pendientes y vencidos
"""

# dataclass para las clases de datos del módulo
from dataclasses import dataclass

# Optional para valores que pueden ser None
from typing import Optional

# date para trabajar con fechas de entrega
from datetime import date, datetime

# Context manager de conexión a PostgreSQL
from db.connection import db_cursor


# ── Dataclass Proveedor ────────────────────────────────────────────────────────
@dataclass
class Proveedor:
    """Representa un proveedor registrado en el sistema."""
    id:       int   # PK de la tabla proveedores
    nombre:   str   # Razón social o nombre comercial
    contacto: str   # Nombre del representante de ventas
    telefono: str   # Número de contacto directo
    email:    str   # Correo electrónico
    nit:      str   # NIT o RUT del proveedor (único)
    activo:   bool  # False = proveedor dado de baja


# ── Dataclass Pedido ───────────────────────────────────────────────────────────
@dataclass
class Pedido:
    """Representa un pedido (orden de compra) a un proveedor."""
    id:              int       # PK de la tabla pedidos
    numero_pedido:   str       # Número único generado automáticamente
    proveedor_id:    int       # FK al proveedor
    proveedor_nombre: str      # Nombre del proveedor (via JOIN)
    usuario_id:      int       # FK al usuario que creó el pedido
    usuario_nombre:  str       # Nombre del usuario (via JOIN)
    fecha_pedido:    datetime  # Fecha y hora de creación
    fecha_estimada:  date      # Fecha prometida de entrega
    estado:          str       # 'Pendiente' | 'Recibido' | 'Cancelado'
    notas:           str       # Observaciones adicionales


# ── CRUD Proveedores ───────────────────────────────────────────────────────────

def listar_proveedores(solo_activos: bool = True) -> list[Proveedor]:
    """
    Retorna todos los proveedores ordenados por nombre.
    Si solo_activos=True, excluye los proveedores dados de baja.
    """
    with db_cursor() as cur:
        if solo_activos:
            # Filtramos por activo=TRUE
            cur.execute("""
                SELECT id, nombre, contacto, telefono, email, nit, activo
                FROM proveedores
                WHERE activo = TRUE
                ORDER BY nombre
            """)
        else:
            # Retornamos todos sin filtrar
            cur.execute("""
                SELECT id, nombre, contacto, telefono, email, nit, activo
                FROM proveedores
                ORDER BY nombre
            """)
        # Instanciamos Proveedor para cada fila retornada
        return [Proveedor(**dict(r)) for r in cur.fetchall()]


def registrar_proveedor(nombre: str, contacto: str, telefono: str,
                        email: str, nit: str) -> tuple[bool, str]:
    """
    Inserta un nuevo proveedor en la base de datos.
    El NIT es único; si ya existe, retornamos error descriptivo.
    Retorna (exito: bool, mensaje: str).
    """
    # Validación: el nombre es el único campo obligatorio
    if not nombre.strip():
        return False, "El nombre del proveedor es obligatorio."

    try:
        with db_cursor(commit=True) as cur:
            cur.execute("""
                INSERT INTO proveedores (nombre, contacto, telefono, email, nit)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre.strip(), contacto.strip(), telefono.strip(),
                  email.strip(), nit.strip() or None))
            # nit.strip() or None → si el campo está vacío, guardamos NULL

        return True, "Proveedor registrado correctamente."

    except Exception as e:
        # La restricción UNIQUE del NIT lanzará este error
        if "unique" in str(e).lower():
            return False, "Ya existe un proveedor con ese NIT."
        return False, f"Error: {e}"


def actualizar_proveedor(pid: int, nombre: str, contacto: str,
                         telefono: str, email: str) -> tuple[bool, str]:
    """
    Actualiza los datos de contacto de un proveedor existente.
    No se permite editar el NIT para preservar la trazabilidad.
    """
    if not nombre.strip():
        return False, "El nombre es obligatorio."

    try:
        with db_cursor(commit=True) as cur:
            cur.execute("""
                UPDATE proveedores
                SET nombre=%s, contacto=%s, telefono=%s, email=%s
                WHERE id=%s
            """, (nombre.strip(), contacto.strip(), telefono.strip(),
                  email.strip(), pid))
        return True, "Proveedor actualizado."
    except Exception as e:
        return False, f"Error: {e}"


def desactivar_proveedor(pid: int) -> tuple[bool, str]:
    """
    Desactiva un proveedor (borrado lógico).
    Los pedidos históricos vinculados a este proveedor se conservan.
    """
    with db_cursor(commit=True) as cur:
        cur.execute("UPDATE proveedores SET activo=FALSE WHERE id=%s", (pid,))
    return True, "Proveedor desactivado."


# ── Número de pedido ────────────────────────────────────────────────────────
def _generar_numero_pedido() -> str:
    """
    Genera un número único para el pedido con formato PED-YYYYMMDD-NNNN.
    Función privada (prefijo _) usada internamente por registrar_pedido.
    """
    with db_cursor() as cur:
        # Contamos los pedidos existentes para el correlativo
        cur.execute("SELECT COUNT(*) AS total FROM pedidos")
        n = cur.fetchone()["total"] + 1

    # Fecha actual sin separadores para mantener el número compacto
    fecha = datetime.now().strftime("%Y%m%d")
    return f"PED-{fecha}-{n:04d}"


# ── Registro de pedidos (HU-06) ────────────────────────────────────────────────

def registrar_pedido(proveedor_id: int, usuario_id: int,
                     fecha_estimada: date,
                     items: list[dict],
                     notas: str = "") -> tuple[bool, str, Optional[int]]:
    """
    Registra un pedido a proveedor con sus ítems de forma atómica.
    Parámetros:
        proveedor_id:   ID del proveedor seleccionado
        usuario_id:     ID del usuario que genera el pedido
        fecha_estimada: Fecha prometida de entrega (objeto date)
        items:          Lista de dicts con keys: producto_id, cantidad, precio_ref
        notas:          Observaciones opcionales
    Retorna (exito: bool, numero_pedido | mensaje_error: str, pedido_id | None).
    """
    # Validación: debe haber al menos un ítem en el pedido
    if not items:
        return False, "El pedido debe tener al menos un producto.", None

    # Validación: la fecha de entrega debe ser futura o igual a hoy
    if fecha_estimada < date.today():
        return False, "La fecha estimada no puede ser en el pasado.", None

    # Generamos el número de pedido antes de abrir la transacción
    numero = _generar_numero_pedido()

    try:
        with db_cursor(commit=True) as cur:
            # ── Insertar cabecera del pedido ──────────────────────────────────
            cur.execute("""
                INSERT INTO pedidos
                    (numero_pedido, proveedor_id, usuario_id, fecha_estimada,
                     estado, notas)
                VALUES (%s, %s, %s, %s, 'Pendiente', %s)
                RETURNING id
            """, (numero, proveedor_id, usuario_id, fecha_estimada, notas))
            pedido_id = cur.fetchone()["id"]

            # ── Insertar ítems del detalle del pedido ─────────────────────────
            for item in items:
                cur.execute("""
                    INSERT INTO pedido_detalles
                        (pedido_id, producto_id, cantidad, precio_ref)
                    VALUES (%s, %s, %s, %s)
                """, (pedido_id,
                      item["producto_id"],    # ID del producto solicitado
                      item["cantidad"],        # Unidades a pedir
                      item.get("precio_ref"))) # Precio de referencia (puede ser None)

        return True, numero, pedido_id

    except Exception as e:
        return False, f"Error al registrar pedido: {e}", None


def listar_pedidos(estado: Optional[str] = None) -> list[dict]:
    """
    Retorna pedidos con datos del proveedor y creador.
    Si estado es None, retorna todos los estados.
    Estados válidos: 'Pendiente', 'Recibido', 'Cancelado'.
    """
    with db_cursor() as cur:
        if estado:
            # Filtramos por un estado específico
            cur.execute("""
                SELECT p.id, p.numero_pedido, p.fecha_pedido,
                       p.fecha_estimada, p.estado, p.notas,
                       pr.nombre AS proveedor_nombre,
                       u.nombre  AS usuario_nombre
                FROM pedidos p
                JOIN proveedores pr ON pr.id = p.proveedor_id
                JOIN usuarios    u  ON u.id  = p.usuario_id
                WHERE p.estado = %s
                ORDER BY p.fecha_pedido DESC  -- Los más recientes primero
            """, (estado,))
        else:
            # Retornamos todos los pedidos sin filtro de estado
            cur.execute("""
                SELECT p.id, p.numero_pedido, p.fecha_pedido,
                       p.fecha_estimada, p.estado, p.notas,
                       pr.nombre AS proveedor_nombre,
                       u.nombre  AS usuario_nombre
                FROM pedidos p
                JOIN proveedores pr ON pr.id = p.proveedor_id
                JOIN usuarios    u  ON u.id  = p.usuario_id
                ORDER BY p.fecha_pedido DESC
            """)
        return [dict(r) for r in cur.fetchall()]


def obtener_pedido_detalle(pedido_id: int) -> Optional[dict]:
    """
    Retorna la cabecera de un pedido junto con sus ítems detallados.
    Incluye el nombre y código de cada producto solicitado.
    Retorna None si el pedido no existe.
    """
    with db_cursor() as cur:
        # Cabecera con datos de proveedor y creador
        cur.execute("""
            SELECT p.id, p.numero_pedido, p.fecha_pedido,
                   p.fecha_estimada, p.estado, p.notas,
                   pr.nombre AS proveedor_nombre,
                   u.nombre  AS usuario_nombre
            FROM pedidos p
            JOIN proveedores pr ON pr.id = p.proveedor_id
            JOIN usuarios    u  ON u.id  = p.usuario_id
            WHERE p.id = %s
        """, (pedido_id,))
        row = cur.fetchone()

        if not row:
            return None  # El pedido no existe

        pedido = dict(row)  # Convertimos a dict mutable para agregar detalles

        # Ítems del detalle con nombre y código del producto
        cur.execute("""
            SELECT pd.cantidad, pd.precio_ref,
                   pr.id AS producto_id, pr.codigo, pr.nombre AS producto_nombre
            FROM pedido_detalles pd
            JOIN productos pr ON pr.id = pd.producto_id
            WHERE pd.pedido_id = %s
        """, (pedido_id,))
        pedido["items"] = [dict(r) for r in cur.fetchall()]

    return pedido


def actualizar_estado_pedido(pedido_id: int, nuevo_estado: str) -> tuple[bool, str]:
    """
    Cambia el estado de un pedido.
    Estados permitidos: 'Pendiente', 'Recibido', 'Cancelado'.
    Si el estado es 'Recibido', incrementa el stock de cada producto pedido.
    """
    # Validamos que el estado sea uno de los permitidos
    estados_validos = ("Pendiente", "Recibido", "Cancelado")
    if nuevo_estado not in estados_validos:
        return False, f"Estado inválido. Opciones: {', '.join(estados_validos)}."

    with db_cursor(commit=True) as cur:
        # Actualizamos el estado del pedido en la cabecera
        cur.execute("""
            UPDATE pedidos SET estado=%s WHERE id=%s
        """, (nuevo_estado, pedido_id))

        if nuevo_estado == "Recibido":
            # Cuando el pedido llega, sumamos las cantidades al stock de cada producto
            cur.execute("""
                SELECT producto_id, cantidad FROM pedido_detalles WHERE pedido_id=%s
            """, (pedido_id,))
            items = cur.fetchall()  # Ítems del pedido recibido

            for item in items:
                # Incrementamos el stock_actual con la cantidad recibida
                cur.execute("""
                    UPDATE productos
                    SET stock_actual = stock_actual + %s, actualizado_en = NOW()
                    WHERE id = %s
                """, (item["cantidad"], item["producto_id"]))

    return True, f"Pedido marcado como '{nuevo_estado}'."


def pedidos_pendientes_vencidos() -> list[dict]:
    """
    Retorna pedidos con estado 'Pendiente' cuya fecha_estimada ya pasó.
    Usado para mostrar una alerta de pedidos atrasados en el dashboard.
    """
    with db_cursor() as cur:
        cur.execute("""
            SELECT p.id, p.numero_pedido, p.fecha_estimada,
                   pr.nombre AS proveedor_nombre
            FROM pedidos p
            JOIN proveedores pr ON pr.id = p.proveedor_id
            WHERE p.estado = 'Pendiente'
              AND p.fecha_estimada < CURRENT_DATE  -- Solo los que ya vencieron
            ORDER BY p.fecha_estimada ASC  -- Los más atrasados primero
        """)
        return [dict(r) for r in cur.fetchall()]
