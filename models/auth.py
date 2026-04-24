"""
AutoParts Express - Modelo de Autenticación y Usuarios
HU-01: Inicio de Sesión
"""
import bcrypt
from dataclasses import dataclass
from typing import Optional
from db.connection import db_cursor


@dataclass
class Usuario:
    id: int
    cedula: str
    nombre: str
    username: str
    rol: str
    activo: bool
    bloqueado: bool


# ── Sesión global activa ────────────────────────────────────────────────────
_sesion_activa: Optional[Usuario] = None


def get_usuario_activo() -> Optional[Usuario]:
    return _sesion_activa


def set_usuario_activo(u: Optional[Usuario]):
    global _sesion_activa
    _sesion_activa = u


# ── Autenticación ───────────────────────────────────────────────────────────
MAX_INTENTOS = 3


def iniciar_sesion(username: str, password: str) -> tuple[bool, str, Optional[Usuario]]:
    """
    Valida credenciales.
    Retorna (exito, mensaje, usuario|None)
    """
    if not username.strip() or not password.strip():
        return False, "Por favor completa todos los campos.", None

    with db_cursor(commit=True) as cur:
        cur.execute("""
            SELECT u.id, u.cedula, u.nombre, u.username,
                   u.password_hash, u.activo, u.bloqueado,
                   u.intentos_fallidos, r.nombre AS rol
            FROM usuarios u
            JOIN roles r ON r.id = u.rol_id
            WHERE u.username = %s
        """, (username.strip(),))
        row = cur.fetchone()

    if not row:
        return False, "Usuario o contraseña incorrectos.", None

    if row["bloqueado"]:
        return False, "Tu cuenta está bloqueada. Contacta al administrador.", None

    if not row["activo"]:
        return False, "Tu cuenta está inactiva.", None

    # Verificar contraseña
    pw_ok = bcrypt.checkpw(password.encode(), row["password_hash"].encode())

    if not pw_ok:
        nuevos_intentos = row["intentos_fallidos"] + 1
        bloquear = nuevos_intentos >= MAX_INTENTOS
        with db_cursor(commit=True) as cur:
            cur.execute("""
                UPDATE usuarios
                SET intentos_fallidos = %s, bloqueado = %s
                WHERE id = %s
            """, (nuevos_intentos, bloquear, row["id"]))

        restantes = MAX_INTENTOS - nuevos_intentos
        if bloquear:
            return False, "Cuenta bloqueada por demasiados intentos fallidos.", None
        return False, f"Contraseña incorrecta. Intentos restantes: {restantes}.", None

    # Éxito: resetear intentos y registrar sesión
    with db_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE usuarios SET intentos_fallidos = 0, bloqueado = FALSE
            WHERE id = %s
        """, (row["id"],))
        cur.execute("""
            INSERT INTO sesiones (usuario_id) VALUES (%s)
        """, (row["id"],))

    usuario = Usuario(
        id=row["id"],
        cedula=row["cedula"],
        nombre=row["nombre"],
        username=row["username"],
        rol=row["rol"],
        activo=row["activo"],
        bloqueado=False,
    )
    set_usuario_activo(usuario)
    return True, f"Bienvenido, {usuario.nombre}.", usuario


def cerrar_sesion():
    set_usuario_activo(None)


# ── Gestión de usuarios (HU-08 - Sprint 2) ─────────────────────────────────
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def crear_usuario(cedula: str, nombre: str, username: str,
                  password: str, rol_nombre: str) -> tuple[bool, str]:
    try:
        ph = hash_password(password)
        with db_cursor(commit=True) as cur:
            cur.execute("SELECT id FROM roles WHERE nombre = %s", (rol_nombre,))
            rol = cur.fetchone()
            if not rol:
                return False, f"Rol '{rol_nombre}' no encontrado."
            cur.execute("""
                INSERT INTO usuarios (cedula, nombre, username, password_hash, rol_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (cedula, nombre, username, ph, rol["id"]))
        return True, "Usuario creado exitosamente."
    except Exception as e:
        if "unique" in str(e).lower():
            return False, "Ya existe un usuario con esa cédula o nombre de usuario."
        return False, f"Error: {e}"


def listar_roles() -> list[str]:
    with db_cursor() as cur:
        cur.execute("SELECT nombre FROM roles ORDER BY nombre")
        return [r["nombre"] for r in cur.fetchall()]
