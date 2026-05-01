"""
AutoParts Express - Modelo de Inventario
HU-02: Registro de Producto
HU-03: Búsqueda y Filtrado
"""
from dataclasses import dataclass
from typing import Optional
from db.connection import db_cursor


@dataclass
class Producto:
    id: int
    codigo: str
    nombre: str
    descripcion: str
    categoria: str
    categoria_id: int
    precio_unitario: float
    stock_actual: int
    stock_minimo: int
    activo: bool


# ── Categorías ──────────────────────────────────────────────────────────────
def listar_categorias() -> list[dict]:
    with db_cursor() as cur:
        cur.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
        return [dict(r) for r in cur.fetchall()]


# ── CRUD Productos ──────────────────────────────────────────────────────────
def registrar_producto(codigo: str, nombre: str, descripcion: str,
                       categoria_id: int, precio: float,
                       stock_inicial: int, stock_minimo: int) -> tuple[bool, str]:
    if not codigo.strip() or not nombre.strip():
        return False, "Código y nombre son obligatorios."
    if precio < 0:
        return False, "El precio no puede ser negativo."
    if stock_inicial < 0 or stock_minimo < 0:
        return False, "El stock no puede ser negativo."
    try:
        with db_cursor(commit=True) as cur:
            cur.execute("""
                INSERT INTO productos
                    (codigo, nombre, descripcion, categoria_id,
                     precio_unitario, stock_actual, stock_minimo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (codigo.strip(), nombre.strip(), descripcion.strip(),
                  categoria_id, precio, stock_inicial, stock_minimo))
            new_id = cur.fetchone()["id"]
        return True, f"Producto registrado con ID {new_id}."
    except Exception as e:
        if "unique" in str(e).lower():
            return False, f"Ya existe un producto con el código '{codigo}'."
        return False, f"Error al guardar: {e}"


def actualizar_producto(pid: int, nombre: str, descripcion: str,
                        categoria_id: int, precio: float,
                        stock_minimo: int) -> tuple[bool, str]:
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
    if nueva_cantidad < 0:
        return False, "El stock no puede ser negativo."
    with db_cursor(commit=True) as cur:
        cur.execute("UPDATE productos SET stock_actual=%s, actualizado_en=NOW() WHERE id=%s",
                    (nueva_cantidad, pid))
    return True, "Stock actualizado."


def desactivar_producto(pid: int) -> tuple[bool, str]:
    with db_cursor(commit=True) as cur:
        cur.execute("UPDATE productos SET activo=FALSE WHERE id=%s", (pid,))
    return True, "Producto eliminado del catálogo."


# ── Búsqueda / Filtrado (HU-03) ─────────────────────────────────────────────
def buscar_productos(texto: str = "", categoria_id: Optional[int] = None,
                     solo_activos: bool = True) -> list[Producto]:
    """
    Busca productos por texto (nombre o código) y/o categoría.
    Retorna en < 2 segundos gracias a índices en BD.
    """
    conditions = []
    params = []

    if solo_activos:
        conditions.append("p.activo = TRUE")

    if texto.strip():
        conditions.append("(LOWER(p.nombre) LIKE %s OR LOWER(p.codigo) LIKE %s)")
        like = f"%{texto.strip().lower()}%"
        params += [like, like]

    if categoria_id:
        conditions.append("p.categoria_id = %s")
        params.append(categoria_id)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    with db_cursor() as cur:
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
        return [Producto(**dict(r)) for r in cur.fetchall()]


def obtener_producto(pid: int) -> Optional[Producto]:
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
        return Producto(**dict(row)) if row else None


def productos_stock_bajo() -> list[Producto]:
    """Retorna productos donde stock_actual <= stock_minimo."""
    with db_cursor() as cur:
        cur.execute("""
            SELECT p.id, p.codigo, p.nombre, p.descripcion,
                   c.nombre AS categoria, p.categoria_id,
                   p.precio_unitario, p.stock_actual, p.stock_minimo, p.activo
            FROM productos p
            LEFT JOIN categorias c ON c.id = p.categoria_id
            WHERE p.activo = TRUE AND p.stock_actual <= p.stock_minimo
            ORDER BY p.stock_actual
        """)
        return [Producto(**dict(r)) for r in cur.fetchall()]
