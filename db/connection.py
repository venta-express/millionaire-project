"""
AutoParts Express - Gestor de conexiÃ³n a PostgreSQL
Sprint 3: Credenciales movidas a variables de entorno (fix SonarCloud).
Provee get_connection(), db_cursor() e init_db() para toda la app.
"""

import os
import psycopg2
import psycopg2.extras
from contextlib import contextmanager

# â”€â”€ ConfiguraciÃ³n de la base de datos â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Las credenciales se leen desde variables de entorno para evitar hardcodeo.
# Configura en tu sistema operativo o en un archivo .env (con python-dotenv):
#   export DB_HOST=localhost
#   export DB_PORT=5432
#   export DB_NAME=autoparts_db
#   export DB_USER=postgres
#   export DB_PASSWORD=tu_contraseÃ±a_segura
DB_CONFIG = {
    "host":     os.environ.get("DB_HOST", "localhost"),
    "port":     int(os.environ.get("DB_PORT", "5432")),
    "dbname":   os.environ.get("DB_NAME", "autoparts_db"),
    "user":     os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "cesar453"),  # Valor por defecto para desarrollo, no recomendado en producciÃ³n
}


def get_connection():
    """
    Abre y retorna una conexiÃ³n nueva al servidor PostgreSQL.
    Cada llamada crea una conexiÃ³n independiente (sin pool).
    """
    return psycopg2.connect(**DB_CONFIG)


@contextmanager
def db_cursor(commit: bool = False):
    """
    Context manager que entrega un cursor listo para ejecutar SQL.
    ParÃ¡metros:
        commit: si True, hace COMMIT al terminar el bloque 'with'.
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
    """
    Lee el archivo schema.sql y lo ejecuta contra la base de datos.
    """
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="latin-1") as f:
        sql = f.read()
    with db_cursor(commit=True) as cur:
        cur.execute(sql)
    print("âœ… Base de datos inicializada correctamente (Sprint 3).")


def test_connection() -> bool:
    """
    Verifica que la base de datos sea accesible.
    Retorna True si la conexiÃ³n funciona, False en caso contrario.
    """
    try:
        with db_cursor() as cur:
            cur.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"âŒ Error de conexiÃ³n: {e}")
        return False

