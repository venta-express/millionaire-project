"""
AutoParts Express - Gestor de conexión a PostgreSQL
Sprint 2: Sin cambios estructurales respecto al Sprint 1.
Provee get_connection(), db_cursor() e init_db() para toda la app.
"""

# Importamos psycopg2, el driver oficial de PostgreSQL para Python
import psycopg2

# extras nos da el cursor RealDictCursor que devuelve filas como diccionarios
import psycopg2.extras

# contextmanager permite crear context managers con la sintaxis 'with'
from contextlib import contextmanager

# ── Configuración de la base de datos ─────────────────────────────────────────
# Diccionario con los parámetros de conexión; se pasan como **kwargs a psycopg2
DB_CONFIG = {
    "host":     "localhost",          # Servidor donde corre PostgreSQL
    "port":     5432,                 # Puerto estándar de PostgreSQL
    "dbname":   "autoparts_db",       # Nombre de la base de datos
    "user":     "postgres",           # Usuario de PostgreSQL
    "password": "M@ichelsboy@07",     # Contraseña; cambia según tu instalación
}


def get_connection():
    """
    Abre y retorna una conexión nueva al servidor PostgreSQL.
    Cada llamada crea una conexión independiente (sin pool).
    """
    # psycopg2.connect() acepta parámetros nombrados del diccionario DB_CONFIG
    return psycopg2.connect(**DB_CONFIG)


@contextmanager
def db_cursor(commit: bool = False):
    """
    Context manager que entrega un cursor listo para ejecutar SQL.
    Parámetros:
        commit: si True, hace COMMIT al terminar el bloque 'with'.
    Uso:
        with db_cursor(commit=True) as cur:
            cur.execute("INSERT ...")
    """
    # Abrimos una conexión nueva para este bloque
    conn = get_connection()
    try:
        # RealDictCursor hace que cada fila sea accesible como dict (row["col"])
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Cedemos el cursor al código del bloque 'with'
        yield cur

        # Si se pidió commit y no hubo excepciones, confirmamos la transacción
        if commit:
            conn.commit()

    except Exception:
        # Ante cualquier error revertimos todos los cambios de la transacción
        conn.rollback()

        # Re-lanzamos la excepción para que el llamador pueda manejarla
        raise

    finally:
        # Cerramos la conexión pase lo que pase (éxito o error)
        conn.close()


def init_db():
    """
    Lee el archivo schema.sql y lo ejecuta contra la base de datos.
    Crea tablas (incluyendo las nuevas del Sprint 2) e inserta datos base.
    Llámalo una vez al configurar el entorno o al actualizar el esquema.
    """
    import os  # os.path para construir la ruta al schema de forma portátil

    # Construimos la ruta absoluta al archivo schema.sql junto a este módulo
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

    # Leemos el SQL completo en memoria
    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()

    # Ejecutamos el script SQL en una sola transacción con commit
    with db_cursor(commit=True) as cur:
        cur.execute(sql)

    print("✅ Base de datos inicializada correctamente (Sprint 2).")


def test_connection() -> bool:
    """
    Verifica que la base de datos sea accesible.
    Retorna True si la conexión funciona, False en caso contrario.
    Usado en main.py antes de mostrar la ventana de login.
    """
    try:
        # Ejecutamos una consulta trivial solo para probar la conectividad
        with db_cursor() as cur:
            cur.execute("SELECT 1")
        return True  # Llegamos aquí → conexión exitosa

    except Exception as e:
        # Imprimimos el error para diagnóstico en consola
        print(f"❌ Error de conexión: {e}")
        return False  # Retornamos False para que main.py lo maneje
