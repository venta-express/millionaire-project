"""
AutoParts Express - Gestor de conexión a PostgreSQL
"""
import psycopg2
import psycopg2.extras
from contextlib import contextmanager

# ── Configuración ──────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "autoparts_db",
    "user":     "postgres",
    "password": "M@ichelsboy@07",   # ← cambia esto por tu contraseña real de pgAdmin
}

def get_connection():
    """Retorna una conexión nueva al servidor PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


@contextmanager
def db_cursor(commit: bool = False):
    """
    Context manager que entrega un cursor y opcionalmente hace commit.
    Uso:
        with db_cursor(commit=True) as cur:
            cur.execute(...)
    """
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Ejecuta el schema SQL para crear tablas e insertar datos base."""
    import os
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()
    with db_cursor(commit=True) as cur:
        cur.execute(sql)
    print("✅ Base de datos inicializada correctamente.")


def test_connection() -> bool:
    """Comprueba que la BD sea accesible. Retorna True/False."""
    try:
        with db_cursor() as cur:
            cur.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
