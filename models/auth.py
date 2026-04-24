"""
AutoParts Express - Modelo de Autenticación y Usuarios
HU-01: Inicio de Sesión  (Sprint 1, sin cambios)
HU-08: Gestión de Usuarios y Roles (Sprint 2 - nuevo)

Responsabilidades:
  - Autenticar usuarios (iniciar_sesion)
  - Mantener la sesión activa global (_sesion_activa)
  - Crear, listar, editar y desactivar usuarios (solo Gerencia)
"""

# bcrypt: librería para hashing seguro de contraseñas (algoritmo Blowfish)
import bcrypt

# dataclass genera automáticamente __init__, __repr__ y __eq__ para la clase
from dataclasses import dataclass

# Optional indica que un valor puede ser del tipo indicado o None
from typing import Optional

# Importamos nuestro context manager de conexión a la BD
from db.connection import db_cursor


# ── Dataclass Usuario ─────────────────────────────────────────────────────────
@dataclass
class Usuario:
    """Representa un usuario autenticado o listado desde la BD."""
    id: int          # PK de la tabla usuarios
    cedula: str      # Documento de identidad
    nombre: str      # Nombre completo
    username: str    # Nombre de usuario para login
    rol: str         # Nombre del rol (Gerencia, Vendedor, Inventario)
    activo: bool     # True = cuenta habilitada
    bloqueado: bool  # True = cuenta bloqueada por intentos fallidos


# ── Sesión global activa ──────────────────────────────────────────────────────
# Variable módulo-nivel que guarda el usuario autenticado en la sesión actual
# None cuando no hay nadie logueado; se actualiza al loguear/desloguear
_sesion_activa: Optional[Usuario] = None


def get_usuario_activo() -> Optional[Usuario]:
    """Retorna el usuario actualmente logueado, o None si no hay sesión."""
    return _sesion_activa  # Acceso de solo lectura a la sesión global


def set_usuario_activo(u: Optional[Usuario]):
    """Establece (o limpia) el usuario de la sesión global."""
    global _sesion_activa  # Necesario para modificar la variable de módulo
    _sesion_activa = u


# ── Constante de seguridad ────────────────────────────────────────────────────
# Número máximo de contraseñas incorrectas antes de bloquear la cuenta
MAX_INTENTOS = 3


# ── Autenticación (HU-01) ─────────────────────────────────────────────────────
def iniciar_sesion(username: str, password: str) -> tuple[bool, str, Optional[Usuario]]:
    """
    Valida credenciales y abre una sesión si son correctas.
    Retorna: (exito: bool, mensaje: str, usuario | None)
    """
    # Validación básica: los campos no pueden estar vacíos
    if not username.strip() or not password.strip():
        return False, "Por favor completa todos los campos.", None

    # Consultamos el usuario junto a su rol en una sola query con JOIN
    with db_cursor(commit=True) as cur:
        cur.execute("""
            SELECT u.id, u.cedula, u.nombre, u.username,
                   u.password_hash, u.activo, u.bloqueado,
                   u.intentos_fallidos, r.nombre AS rol
            FROM usuarios u
            JOIN roles r ON r.id = u.rol_id
            WHERE u.username = %s
        """, (username.strip(),))
        row = cur.fetchone()  # fetchone() retorna la primera fila o None

    # Si no existe el username, respondemos con mensaje genérico (evita enumerar usuarios)
    if not row:
        return False, "Usuario o contraseña incorrectos.", None

    # Si la cuenta está bloqueada, impedimos el acceso
    if row["bloqueado"]:
        return False, "Tu cuenta está bloqueada. Contacta al administrador.", None

    # Si la cuenta está inactiva, también impedimos el acceso
    if not row["activo"]:
        return False, "Tu cuenta está inactiva.", None

    # Comparamos la contraseña ingresada con el hash almacenado
    # bcrypt.checkpw() maneja el salt internamente
    pw_ok = bcrypt.checkpw(password.encode(), row["password_hash"].encode())

    if not pw_ok:
        # Incrementamos el contador de intentos fallidos
        nuevos_intentos = row["intentos_fallidos"] + 1

        # Determinamos si ya se alcanzó el límite de intentos
        bloquear = nuevos_intentos >= MAX_INTENTOS

        # Actualizamos la BD con el nuevo contador y posible bloqueo
        with db_cursor(commit=True) as cur:
            cur.execute("""
                UPDATE usuarios
                SET intentos_fallidos = %s, bloqueado = %s
                WHERE id = %s
            """, (nuevos_intentos, bloquear, row["id"]))

        # Calculamos cuántos intentos le quedan al usuario
        restantes = MAX_INTENTOS - nuevos_intentos

        if bloquear:
            # Cuenta bloqueada definitivamente
            return False, "Cuenta bloqueada por demasiados intentos fallidos.", None

        # Informamos al usuario cuántos intentos le restan
        return False, f"Contraseña incorrecta. Intentos restantes: {restantes}.", None

    # ── Login exitoso ────────────────────────────────────────────────────────
    # Reseteamos el contador de intentos fallidos y desbloqueamos si estaba bloqueado
    with db_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE usuarios SET intentos_fallidos = 0, bloqueado = FALSE
            WHERE id = %s
        """, (row["id"],))

        # Registramos la sesión en la tabla de auditoría
        cur.execute("""
            INSERT INTO sesiones (usuario_id) VALUES (%s)
        """, (row["id"],))

    # Construimos el objeto Usuario con los datos de la fila
    usuario = Usuario(
        id=row["id"],
        cedula=row["cedula"],
        nombre=row["nombre"],
        username=row["username"],
        rol=row["rol"],
        activo=row["activo"],
        bloqueado=False,  # Acabamos de asegurarnos de que no está bloqueado
    )

    # Guardamos el usuario en la sesión global de la aplicación
    set_usuario_activo(usuario)

    return True, f"Bienvenido, {usuario.nombre}.", usuario


def cerrar_sesion():
    """Limpia la sesión activa global al hacer logout."""
    set_usuario_activo(None)  # Poner None desloguea al usuario


# ── Utilidades de contraseña ──────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    """
    Genera un hash bcrypt seguro para la contraseña en texto plano.
    bcrypt.gensalt() genera un salt aleatorio de 12 rondas por defecto.
    """
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


# ── Gestión de usuarios (HU-08 - Sprint 2) ───────────────────────────────────

def listar_usuarios() -> list[dict]:
    """
    Retorna todos los usuarios del sistema con su rol.
    Usado en la pantalla de gestión de usuarios (solo Gerencia).
    """
    with db_cursor() as cur:
        # JOIN para traer el nombre del rol en lugar del ID
        cur.execute("""
            SELECT u.id, u.cedula, u.nombre, u.username,
                   r.nombre AS rol, u.activo, u.bloqueado,
                   u.creado_en
            FROM usuarios u
            JOIN roles r ON r.id = u.rol_id
            ORDER BY u.nombre  -- Orden alfabético para la tabla de la UI
        """)
        # Convertimos cada RealDictRow a dict plano para facilitar su uso en la UI
        return [dict(r) for r in cur.fetchall()]


def crear_usuario(cedula: str, nombre: str, username: str,
                  password: str, rol_nombre: str) -> tuple[bool, str]:
    """
    Crea un nuevo usuario con el rol indicado.
    Retorna (exito: bool, mensaje: str).
    Solo accesible para usuarios con rol 'Gerencia'.
    """
    try:
        # Generamos el hash de la contraseña antes de guardar
        ph = hash_password(password)

        with db_cursor(commit=True) as cur:
            # Buscamos el ID del rol por su nombre
            cur.execute("SELECT id FROM roles WHERE nombre = %s", (rol_nombre,))
            rol = cur.fetchone()

            # Si el rol no existe en la BD, retornamos error
            if not rol:
                return False, f"Rol '{rol_nombre}' no encontrado."

            # Insertamos el nuevo usuario
            cur.execute("""
                INSERT INTO usuarios (cedula, nombre, username, password_hash, rol_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (cedula.strip(), nombre.strip(), username.strip(), ph, rol["id"]))

        return True, "Usuario creado exitosamente."

    except Exception as e:
        # Violación UNIQUE indica que ya existe cédula o username
        if "unique" in str(e).lower():
            return False, "Ya existe un usuario con esa cédula o nombre de usuario."
        return False, f"Error: {e}"


def editar_usuario(uid: int, nombre: str, rol_nombre: str,
                   activo: bool, nueva_password: str = "") -> tuple[bool, str]:
    """
    Actualiza los datos de un usuario existente.
    Si nueva_password es una cadena no vacía, también cambia la contraseña.
    Retorna (exito: bool, mensaje: str).
    """
    try:
        with db_cursor(commit=True) as cur:
            # Obtenemos el ID del nuevo rol
            cur.execute("SELECT id FROM roles WHERE nombre = %s", (rol_nombre,))
            rol = cur.fetchone()
            if not rol:
                return False, f"Rol '{rol_nombre}' no encontrado."

            if nueva_password.strip():
                # Si se proporcionó nueva contraseña, la incluimos en el UPDATE
                ph = hash_password(nueva_password)
                cur.execute("""
                    UPDATE usuarios
                    SET nombre=%s, rol_id=%s, activo=%s, password_hash=%s,
                        bloqueado=FALSE, intentos_fallidos=0
                    WHERE id=%s
                """, (nombre.strip(), rol["id"], activo, ph, uid))
            else:
                # Sin nueva contraseña, solo actualizamos los demás campos
                cur.execute("""
                    UPDATE usuarios
                    SET nombre=%s, rol_id=%s, activo=%s
                    WHERE id=%s
                """, (nombre.strip(), rol["id"], activo, uid))

        return True, "Usuario actualizado correctamente."

    except Exception as e:
        return False, f"Error al actualizar: {e}"


def desbloquear_usuario(uid: int) -> tuple[bool, str]:
    """
    Desbloquea una cuenta y resetea el contador de intentos fallidos.
    Útil cuando el administrador quiere rehabilitar una cuenta bloqueada.
    """
    with db_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE usuarios
            SET bloqueado=FALSE, intentos_fallidos=0
            WHERE id=%s
        """, (uid,))
    return True, "Usuario desbloqueado."


def listar_roles() -> list[str]:
    """
    Retorna los nombres de todos los roles disponibles.
    Usado para llenar los ComboBox de rol en los formularios.
    """
    with db_cursor() as cur:
        cur.execute("SELECT nombre FROM roles ORDER BY nombre")
        # Extraemos solo el campo 'nombre' de cada fila
        return [r["nombre"] for r in cur.fetchall()]
