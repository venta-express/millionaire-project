"""
AutoParts Express - Modelo de Backup
Sprint 4: Backup y restauracion de la base de datos.
Usa pg_dump para generar respaldos locales en formato SQL.
"""

import os
import subprocess
from datetime import datetime
from db.connection import DB_CONFIG


def generar_backup(directorio: str) -> tuple[bool, str]:
    """
    Genera un backup de la BD usando pg_dump.
    Retorna (exito, ruta_archivo_o_mensaje_error).
    """
    os.makedirs(directorio, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre = f"autoparts_backup_{timestamp}.sql"
    ruta = os.path.join(directorio, nombre)

    env = os.environ.copy()
    env["PGPASSWORD"] = DB_CONFIG["password"]

    cmd = [
        "pg_dump",
        "-h", DB_CONFIG["host"],
        "-p", str(DB_CONFIG["port"]),
        "-U", DB_CONFIG["user"],
        "-d", DB_CONFIG["dbname"],
        "-f", ruta,
        "--no-password",
    ]

    try:
        resultado = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=60
        )
        if resultado.returncode == 0:
            return True, ruta
        else:
            return False, resultado.stderr.strip() or "Error desconocido en pg_dump"
    except FileNotFoundError:
        return False, "pg_dump no encontrado. Asegurate de tener PostgreSQL instalado en PATH."
    except subprocess.TimeoutExpired:
        return False, "El backup tardo demasiado tiempo (timeout 60s)."
    except Exception as e:
        return False, str(e)


def listar_backups(directorio: str) -> list[dict]:
    """Lista los archivos de backup en el directorio."""
    if not os.path.exists(directorio):
        return []
    archivos = []
    for f in os.listdir(directorio):
        if f.startswith("autoparts_backup_") and f.endswith(".sql"):
            ruta = os.path.join(directorio, f)
            stat = os.stat(ruta)
            archivos.append({
                "nombre": f,
                "ruta": ruta,
                "tamano_kb": round(stat.st_size / 1024, 1),
                "fecha": datetime.fromtimestamp(stat.st_mtime),
            })
    return sorted(archivos, key=lambda x: x["fecha"], reverse=True)
