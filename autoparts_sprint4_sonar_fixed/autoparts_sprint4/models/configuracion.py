"""
AutoParts Express - Modelo de Configuracion del Sistema
Sprint 4: Parametros globales configurables por el administrador.
"""

from db.connection import db_cursor


def obtener_config(clave: str, default: str = "") -> str:
    """Obtiene el valor de una clave de configuracion."""
    try:
        with db_cursor() as cur:
            cur.execute("SELECT valor FROM configuracion WHERE clave = %s", (clave,))
            row = cur.fetchone()
            return row["valor"] if row else default
    except Exception:
        return default


def obtener_todas() -> list:
    """Obtiene todas las configuraciones del sistema."""
    with db_cursor() as cur:
        cur.execute("SELECT * FROM configuracion ORDER BY clave")
        return [dict(r) for r in cur.fetchall()]


def actualizar_config(clave: str, valor: str) -> bool:
    """Actualiza o inserta una configuracion."""
    try:
        with db_cursor(commit=True) as cur:
            cur.execute("""
                INSERT INTO configuracion (clave, valor, actualizado_en)
                VALUES (%s, %s, NOW())
                ON CONFLICT (clave) DO UPDATE
                SET valor = EXCLUDED.valor,
                    actualizado_en = NOW()
            """, (clave, valor))
        return True
    except Exception:
        return False


def obtener_info_empresa() -> dict:
    """Obtiene los datos de la empresa para facturas y reportes."""
    with db_cursor() as cur:
        cur.execute("""
            SELECT clave, valor FROM configuracion
            WHERE clave LIKE 'empresa_%' OR clave = 'moneda' OR clave = 'factura_prefijo'
        """)
        return {r["clave"]: r["valor"] for r in cur.fetchall()}
