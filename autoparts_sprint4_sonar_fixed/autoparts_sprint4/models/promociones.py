"""
AutoParts Express - Modelo de Promociones y Descuentos
HU-12: Configuración de Promociones (Sprint 3)

Responsabilidades:
  - CRUD de promociones (solo Gerencia)
  - Calcular el descuento activo para un producto en la fecha actual
  - Aplicar promociones automáticamente al registrar ventas
"""

from dataclasses import dataclass        # Para la clase Promocion
from typing import Optional              # Valores que pueden ser None
from datetime import date as date_type  # Para comparar fechas de vigencia
from db.connection import db_cursor     # Context manager de BD


# ── Dataclass Promocion ───────────────────────────────────────────────────────
@dataclass
class Promocion:
    """Representa una promoción de descuento registrada en el sistema."""
    id:             int         # PK de la tabla promociones
    nombre:         str         # Descripción amigable de la promoción
    tipo_descuento: str         # 'porcentaje' | 'valor_fijo'
    valor:          float       # Monto del descuento (% o valor monetario)
    producto_id:    Optional[int]   # ID del producto objetivo (None si es por categoría)
    categoria_id:   Optional[int]   # ID de la categoría objetivo (None si es por producto)
    fecha_inicio:   date_type   # Primer día de vigencia
    fecha_fin:      date_type   # Último día de vigencia (inclusive)
    activa:         bool        # Permite desactivar sin borrar


# ── Consultas ─────────────────────────────────────────────────────────────────

def listar_promociones(solo_activas: bool = False) -> list[dict]:
    """
    Retorna todas las promociones con el nombre del producto o categoría.
    Si solo_activas=True, filtra solo las vigentes hoy y con activa=TRUE.
    """
    with db_cursor() as cur:
        if solo_activas:
            # Filtramos por activa=TRUE y rango de fechas que incluya hoy
            cur.execute("""
                SELECT p.id, p.nombre, p.tipo_descuento, p.valor,
                       p.producto_id, p.categoria_id,
                       p.fecha_inicio, p.fecha_fin, p.activa,
                       prod.nombre  AS producto_nombre,
                       cat.nombre   AS categoria_nombre
                FROM promociones p
                LEFT JOIN productos   prod ON prod.id = p.producto_id
                LEFT JOIN categorias  cat  ON cat.id  = p.categoria_id
                WHERE p.activa = TRUE
                  AND p.fecha_inicio <= CURRENT_DATE   -- ya empezó
                  AND p.fecha_fin    >= CURRENT_DATE   -- todavía no terminó
                ORDER BY p.fecha_fin ASC               -- las que vencen antes, primero
            """)
        else:
            # Todas las promociones sin filtro
            cur.execute("""
                SELECT p.id, p.nombre, p.tipo_descuento, p.valor,
                       p.producto_id, p.categoria_id,
                       p.fecha_inicio, p.fecha_fin, p.activa,
                       prod.nombre  AS producto_nombre,
                       cat.nombre   AS categoria_nombre
                FROM promociones p
                LEFT JOIN productos   prod ON prod.id = p.producto_id
                LEFT JOIN categorias  cat  ON cat.id  = p.categoria_id
                ORDER BY p.fecha_inicio DESC          -- las más recientes primero
            """)
        return [dict(r) for r in cur.fetchall()]


def calcular_descuento(producto_id: int, precio_unitario: float) -> tuple[float, str]:
    """
    Calcula el descuento vigente hoy para un producto dado.
    Prioridad: descuento por producto > descuento por categoría.
    Retorna (monto_descuento: float, nombre_promo: str).
    Si no hay promoción activa retorna (0.0, "").
    """
    with db_cursor() as cur:
        # Buscamos primero una promoción directa para el producto (prioridad alta)
        cur.execute("""
            SELECT p.nombre, p.tipo_descuento, p.valor
            FROM promociones p
            WHERE p.producto_id = %s
              AND p.activa = TRUE
              AND p.fecha_inicio <= CURRENT_DATE
              AND p.fecha_fin    >= CURRENT_DATE
            ORDER BY p.valor DESC   -- Si hay varias, tomamos la de mayor valor
            LIMIT 1
        """, (producto_id,))
        row = cur.fetchone()

        if not row:
            # No hay promo por producto; buscamos por categoría del producto
            cur.execute("""
                SELECT pr.nombre, pr.tipo_descuento, pr.valor
                FROM promociones pr
                JOIN productos    p ON p.categoria_id = pr.categoria_id
                WHERE p.id = %s
                  AND pr.activa = TRUE
                  AND pr.fecha_inicio <= CURRENT_DATE
                  AND pr.fecha_fin    >= CURRENT_DATE
                ORDER BY pr.valor DESC
                LIMIT 1
            """, (producto_id,))
            row = cur.fetchone()

    if not row:
        return 0.0, ""  # Sin promoción activa para este producto

    # Calculamos el monto según el tipo de descuento
    if row["tipo_descuento"] == "porcentaje":
        # El valor es un porcentaje (ej: 15 significa 15%)
        monto = round(precio_unitario * row["valor"] / 100, 2)
    else:
        # El valor es un monto fijo (ej: 5000 pesos de descuento)
        # No puede superar el precio unitario
        monto = min(float(row["valor"]), precio_unitario)

    return monto, row["nombre"]


def crear_promocion(nombre: str, tipo_descuento: str, valor: float,
                    producto_id: Optional[int], categoria_id: Optional[int],
                    fecha_inicio: date_type, fecha_fin: date_type,
                    creado_por: int) -> tuple[bool, str]:
    """
    Registra una nueva promoción en la base de datos.
    Validaciones:
      - tipo_descuento debe ser 'porcentaje' o 'valor_fijo'
      - valor debe ser > 0
      - Exactamente uno de producto_id o categoria_id debe tener valor
      - fecha_fin >= fecha_inicio
    """
    # Validamos el tipo de descuento
    if tipo_descuento not in ("porcentaje", "valor_fijo"):
        return False, "Tipo de descuento inválido. Use 'porcentaje' o 'valor_fijo'."

    if valor <= 0:
        return False, "El valor del descuento debe ser mayor a cero."

    # Exactamente uno de los dos targets debe estar definido
    if not (bool(producto_id) ^ bool(categoria_id)):
        return False, "Debe especificar un producto O una categoría, no ambos ni ninguno."

    if fecha_fin < fecha_inicio:
        return False, "La fecha de fin debe ser igual o posterior a la fecha de inicio."

    if not nombre.strip():
        return False, "El nombre de la promoción es obligatorio."

    try:
        with db_cursor(commit=True) as cur:
            cur.execute("""
                INSERT INTO promociones
                    (nombre, tipo_descuento, valor, producto_id, categoria_id,
                     fecha_inicio, fecha_fin, creado_por)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nombre.strip(), tipo_descuento, valor,
                  producto_id, categoria_id,
                  fecha_inicio, fecha_fin, creado_por))
        return True, "Promoción creada correctamente."
    except Exception as e:
        return False, f"Error al crear promoción: {e}"


def activar_desactivar_promocion(promo_id: int, activa: bool) -> tuple[bool, str]:
    """
    Activa o desactiva una promoción sin eliminarla.
    Permite pausar una promoción y reactivarla después.
    """
    with db_cursor(commit=True) as cur:
        cur.execute("UPDATE promociones SET activa=%s WHERE id=%s", (activa, promo_id))
    estado = "activada" if activa else "desactivada"
    return True, f"Promoción {estado} correctamente."


def eliminar_promocion(promo_id: int) -> tuple[bool, str]:
    """
    Elimina una promoción definitivamente.
    Solo debe usarse si no tiene ventas asociadas que la referencien.
    """
    with db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM promociones WHERE id=%s", (promo_id,))
    return True, "Promoción eliminada."
