"""
AutoParts Express - Modelo de Inventario
HU-02: Registro de Producto      (Sprint 1, sin cambios)
HU-03: Búsqueda y Filtrado       (Sprint 1, sin cambios)
HU-05: Alertas de Stock Mínimo   (Sprint 2 - nuevo)

Responsabilidades:
  - CRUD completo de productos
  - Búsqueda y filtrado por texto y categoría
  - Generación y consulta de alertas de stock bajo
"""

# dataclass genera automáticamente __init__ y __repr__ para la clase Producto
from dataclasses import dataclass

# Optional para indicar que un valor puede ser None
from typing import Optional

# Context manager de conexión a PostgreSQL definido en db/connection.py
from db.connection import db_cursor


# ── Dataclass Producto ────────────────────────────────────────────────────────
@dataclass
class Producto:
    """Representa un producto del catálogo/inventario."""
    id:              int    # PK en la tabla productos
    codigo:          str    # Código único de referencia (ej: "FRN-001")
    nombre:          str    # Nombre descriptivo del producto
    descripcion:     str    # Descripción larga (puede ser vacía)
    categoria:       str    # Nombre de la categoría (via JOIN)
    categoria_id:    int    # FK a la tabla categorias
    precio_unitario: float  # Precio de venta al público
    stock_actual:    int    # Unidades disponibles en bodega
    stock_minimo:    int    # Umbral mínimo que dispara alertas
    activo:          bool   # False = producto dado de baja (oculto del catálogo)


# ── Categorías ────────────────────────────────────────────────────────────────
def listar_categorias() -> list[dict]:
    """
    Retorna todas las categorías como lista de dicts {id, nombre}.
    Usada para llenar los ComboBox en los formularios de producto.
    """
    with db_cursor() as cur:
        # Ordenamos alfabéticamente para mejor UX en los desplegables
        cur.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
        return [dict(r) for r in cur.fetchall()]  # Convertimos RealDictRow → dict


# ── CRUD Productos ────────────────────────────────────────────────────────────

def registrar_producto(codigo: str, nombre: str, descripcion: str,
                       categoria_id: int, precio: float,
                       stock_inicial: int, stock_minimo: int) -> tuple[bool, str]:
    """
    Inserta un nuevo producto en la base de datos.
    Retorna (exito: bool, mensaje: str).
    Realiza validaciones básicas antes de tocar la BD.
    """
    # Validaciones de negocio: campos obligatorios
    if not codigo.strip() or not nombre.strip():
        return False, "Código y nombre son obligatorios."

    # El precio no puede ser negativo (CHECK de la BD también lo valida)
    if precio < 0:
        return False, "El precio no puede ser negativo."

    # El stock tampoco puede ser negativo
    if stock_inicial < 0 or stock_minimo < 0:
        return False, "El stock no puede ser negativo."

    try:
        with db_cursor(commit=True) as cur:
            # RETURNING id nos devuelve el ID generado por SERIAL
            cur.execute("""
                INSERT INTO productos
                    (codigo, nombre, descripcion, categoria_id,
                     precio_unitario, stock_actual, stock_minimo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (codigo.strip(), nombre.strip(), descripcion.strip(),
                  categoria_id, precio, stock_inicial, stock_minimo))

            new_id = cur.fetchone()["id"]  # ID asignado por PostgreSQL

        return True, f"Producto registrado con ID {new_id}."

    except Exception as e:
        # Error de unicidad: el código ya existe en la BD
        if "unique" in str(e).lower():
            return False, f"Ya existe un producto con el código '{codigo}'."
        return False, f"Error al guardar: {e}"


def actualizar_producto(pid: int, nombre: str, descripcion: str,
                        categoria_id: int, precio: float,
                        stock_minimo: int) -> tuple[bool, str]:
    """
    Actualiza los datos de un producto existente (no modifica el stock_actual).
    Retorna (exito: bool, mensaje: str).
    """
    try:
        with db_cursor(commit=True) as cur:
            cur.execute("""
                UPDATE productos
                SET nombre=%s, descripcion=%s, categoria_id=%s,
                    precio_unitario=%s, stock_minimo=%s, actualizado_en=NOW()
                WHERE id=%s
            """, (nombre, descripcion, categoria_id, precio, stock_minimo, pid))

        return True, "Producto actualizado."

    except Exception as e:
        return False, f"Error: {e}"


def ajustar_stock(pid: int, nueva_cantidad: int) -> tuple[bool, str]:
    """
    Reemplaza el stock_actual de un producto con el valor indicado.
    Usado para ajustes manuales de inventario (conteos físicos).
    Después de ajustar, verifica y registra alerta si aplica.
    """
    # Validación: el stock no puede ser negativo
    if nueva_cantidad < 0:
        return False, "El stock no puede ser negativo."

    with db_cursor(commit=True) as cur:
        # Actualizamos el stock y la fecha de modificación
        cur.execute(
            "UPDATE productos SET stock_actual=%s, actualizado_en=NOW() WHERE id=%s",
            (nueva_cantidad, pid)
        )

    # Sprint 2: verificamos si el nuevo stock activa una alerta
    _registrar_alerta_si_necesario(pid)

    return True, "Stock actualizado."


def desactivar_producto(pid: int) -> tuple[bool, str]:
    """
    Marca un producto como inactivo (borrado lógico).
    El producto deja de aparecer en búsquedas normales pero sus datos se conservan.
    """
    with db_cursor(commit=True) as cur:
        cur.execute("UPDATE productos SET activo=FALSE WHERE id=%s", (pid,))
    return True, "Producto eliminado del catálogo."


# ── Búsqueda / Filtrado (HU-03) ───────────────────────────────────────────────
def buscar_productos(texto: str = "", categoria_id: Optional[int] = None,
                     solo_activos: bool = True) -> list[Producto]:
    """
    Busca productos por texto (nombre o código) y/o categoría.
    El resultado se limita a 200 filas para rendimiento óptimo.
    Retorna en < 2 segundos gracias a índices en BD.
    """
    # Construimos la cláusula WHERE dinámicamente según los filtros activos
    conditions = []  # Lista de fragmentos SQL de condición
    params = []      # Lista de parámetros en el mismo orden que los %s

    if solo_activos:
        # Solo mostramos productos que no han sido dados de baja
        conditions.append("p.activo = TRUE")

    if texto.strip():
        # Búsqueda case-insensitive en nombre y código con LIKE
        conditions.append("(LOWER(p.nombre) LIKE %s OR LOWER(p.codigo) LIKE %s)")
        like = f"%{texto.strip().lower()}%"  # Patrón de búsqueda parcial
        params += [like, like]  # Dos veces porque hay dos columnas en el OR

    if categoria_id:
        # Filtro exacto por categoría (valor entero)
        conditions.append("p.categoria_id = %s")
        params.append(categoria_id)

    # Unimos las condiciones con AND; si no hay ninguna, omitimos el WHERE
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    with db_cursor() as cur:
        # Interpolación segura del WHERE en la query (no hay riesgo de inyección
        # porque 'where' solo contiene nuestros fragmentos, no datos del usuario)
        cur.execute(f"""
            SELECT p.id, p.codigo, p.nombre, p.descripcion,
                   c.nombre AS categoria, p.categoria_id,
                   p.precio_unitario, p.stock_actual, p.stock_minimo, p.activo
            FROM productos p
            LEFT JOIN categorias c ON c.id = p.categoria_id
            {where}
            ORDER BY p.nombre
            LIMIT 200
        """, params)

        # Construimos instancias de Producto a partir de cada fila del resultado
        return [Producto(**dict(r)) for r in cur.fetchall()]


def obtener_producto(pid: int) -> Optional[Producto]:
    """
    Retorna un único producto por su PK, o None si no existe.
    Usado al precargar datos en el formulario de edición.
    """
    with db_cursor() as cur:
        cur.execute("""
            SELECT p.id, p.codigo, p.nombre, p.descripcion,
                   c.nombre AS categoria, p.categoria_id,
                   p.precio_unitario, p.stock_actual, p.stock_minimo, p.activo
            FROM productos p
            LEFT JOIN categorias c ON c.id = p.categoria_id
            WHERE p.id = %s
        """, (pid,))
        row = cur.fetchone()
        # Si hay resultado lo convertimos a Producto, si no retornamos None
        return Producto(**dict(row)) if row else None


def productos_stock_bajo() -> list[Producto]:
    """
    Retorna productos activos cuyo stock_actual <= stock_minimo.
    Usado para el panel de alertas en el módulo de inventario.
    """
    with db_cursor() as cur:
        cur.execute("""
            SELECT p.id, p.codigo, p.nombre, p.descripcion,
                   c.nombre AS categoria, p.categoria_id,
                   p.precio_unitario, p.stock_actual, p.stock_minimo, p.activo
            FROM productos p
            LEFT JOIN categorias c ON c.id = p.categoria_id
            WHERE p.activo = TRUE AND p.stock_actual <= p.stock_minimo
            ORDER BY p.stock_actual  -- Los más críticos primero
        """)
        return [Producto(**dict(r)) for r in cur.fetchall()]


# ── Alertas de Stock Mínimo (HU-05 - Sprint 2) ───────────────────────────────

def _registrar_alerta_si_necesario(pid: int):
    """
    Función privada (prefijo _) que verifica si un producto
    necesita generar una alerta de stock bajo.
    Se llama internamente después de cualquier operación que reduzca el stock.
    """
    with db_cursor(commit=True) as cur:
        # Obtenemos el estado actual del producto
        cur.execute("""
            SELECT stock_actual, stock_minimo FROM productos WHERE id=%s
        """, (pid,))
        row = cur.fetchone()

        if not row:
            return  # El producto no existe; no hacemos nada

        # Condición de alerta: stock actual en o por debajo del mínimo configurado
        if row["stock_actual"] <= row["stock_minimo"]:
            # Insertamos un registro en el historial de alertas
            cur.execute("""
                INSERT INTO alertas_stock (producto_id, stock_actual, stock_minimo)
                VALUES (%s, %s, %s)
            """, (pid, row["stock_actual"], row["stock_minimo"]))


def obtener_alertas_no_vistas() -> list[dict]:
    """
    Retorna todas las alertas de stock que aún no han sido vistas por el usuario.
    Usada al iniciar el módulo de inventario y para el badge de notificaciones.
    """
    with db_cursor() as cur:
        cur.execute("""
            SELECT a.id, a.producto_id, a.stock_actual, a.stock_minimo,
                   a.generada_en, p.codigo, p.nombre AS producto_nombre
            FROM alertas_stock a
            JOIN productos p ON p.id = a.producto_id
            WHERE a.vista = FALSE          -- Solo las no reconocidas
            ORDER BY a.generada_en DESC   -- Las más recientes primero
        """)
        return [dict(r) for r in cur.fetchall()]


def marcar_alertas_vistas():
    """
    Marca todas las alertas pendientes como vistas.
    Se llama cuando el usuario abre el panel de alertas de stock.
    """
    with db_cursor(commit=True) as cur:
        cur.execute("UPDATE alertas_stock SET vista=TRUE WHERE vista=FALSE")
