"""
AutoParts Express - Modelo de AutenticaciÃ³n y Usuarios
HU-01: Inicio de SesiÃ³n  (Sprint 1, sin cambios)
HU-08: GestiÃ³n de Usuarios y Roles (Sprint 2 - nuevo)

Responsabilidades:
  - Autenticar usuarios (iniciar_sesion)
  - Mantener la sesiÃ³n activa global (_sesion_activa)
  - Crear, listar, editar y desactivar usuarios (solo Gerencia)
"""

# bcrypt: librerÃ­a para hashing seguro de contraseÃ±as (algoritmo Blowfish)
import bcrypt

# dataclass genera automÃ¡ticamente __init__, __repr__ y __eq__ para la clase
from dataclasses import dataclass

# Optional indica que un valor puede ser del tipo indicado o None
from typing import Optional

# Importamos nuestro context manager de conexiÃ³n a la BD
from db.connection import db_cursor


# â”€â”€ Dataclass Usuario â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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


# â”€â”€ SesiÃ³n global activa â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Variable mÃ³dulo-nivel que guarda el usuario autenticado en la sesiÃ³n actual
# None cuando no hay nadie logueado; se actualiza al loguear/desloguear
_sesion_activa: Optional[Usuario] = None


def get_usuario_activo() -> Optional[Usuario]:
    """Retorna el usuario actualmente logueado, o None si no hay sesiÃ³n."""
    return _sesion_activa  # Acceso de solo lectura a la sesiÃ³n global


def set_usuario_activo(u: Optional[Usuario]):
    """Establece (o limpia) el usuario de la sesiÃ³n global."""
    global _sesion_activa  # Necesario para modificar la variable de mÃ³dulo
    _sesion_activa = u


# â”€â”€ Constante de seguridad â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# NÃºmero mÃ¡ximo de contraseÃ±as incorrectas antes de bloquear la cuenta
MAX_INTENTOS = 3


# â”€â”€ AutenticaciÃ³n (HU-01) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def iniciar_sesion(username: str, password: str) -> tuple[bool, str, Optional[Usuario]]:
    """
    Valida credenciales y abre una sesiÃ³n si son correctas.
    Retorna: (exito: bool, mensaje: str, usuario | None)
    """
    # ValidaciÃ³n bÃ¡sica: los campos no pueden estar vacÃ­os
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

    # Si no existe el username, respondemos con mensaje genÃ©rico (evita enumerar usuarios)
    if not row:
        return False, "Usuario o contraseÃ±a incorrectos.", None

    # Si la cuenta estÃ¡ bloqueada, impedimos el acceso
    if row["bloqueado"]:
        return False, "Tu cuenta estÃ¡ bloqueada. Contacta al administrador.", None

    # Si la cuenta estÃ¡ inactiva, tambiÃ©n impedimos el acceso
    if not row["activo"]:
        return False, "Tu cuenta estÃ¡ inactiva.", None

    # Comparamos la contraseÃ±a ingresada con el hash almacenado
    # bcrypt.checkpw() maneja el salt internamente
    pw_ok = bcrypt.checkpw(password.encode(), row["password_hash"].encode())

    if not pw_ok:
        # Incrementamos el contador de intentos fallidos
        nuevos_intentos = row["intentos_fallidos"] + 1

        # Determinamos si ya se alcanzÃ³ el lÃ­mite de intentos
        bloquear = nuevos_intentos >= MAX_INTENTOS

        # Actualizamos la BD con el nuevo contador y posible bloqueo
        with db_cursor(commit=True) as cur:
            cur.execute("""
                UPDATE usuarios
                SET intentos_fallidos = %s, bloqueado = %s
                WHERE id = %s
            """, (nuevos_intentos, bloquear, row["id"]))

        # Calculamos cuÃ¡ntos intentos le quedan al usuario
        restantes = MAX_INTENTOS - nuevos_intentos

        if bloquear:
            # Cuenta bloqueada definitivamente
            return False, "Cuenta bloqueada por demasiados intentos fallidos.", None

        # Informamos al usuario cuÃ¡ntos intentos le restan
        return False, f"ContraseÃ±a incorrecta. Intentos restantes: {restantes}.", None

    # â”€â”€ Login exitoso â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Reseteamos el contador de intentos fallidos y desbloqueamos si estaba bloqueado
    with db_cursor(commit=True) as cur:
        cur.execute("""
            UPDATE usuarios SET intentos_fallidos = 0, bloqueado = FALSE
            WHERE id = %s
        """, (row["id"],))

        # Registramos la sesiÃ³n en la tabla de auditorÃ­a
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
        bloqueado=False,  # Acabamos de asegurarnos de que no estÃ¡ bloqueado
    )

    # Guardamos el usuario en la sesiÃ³n global de la aplicaciÃ³n
    set_usuario_activo(usuario)

    return True, f"Bienvenido, {usuario.nombre}.", usuario


def cerrar_sesion():
    """Limpia la sesiÃ³n activa global al hacer logout."""
    set_usuario_activo(None)  # Poner None desloguea al usuario


# â”€â”€ Utilidades de contraseÃ±a â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def hash_password(plain: str) -> str:
    """
    Genera un hash bcrypt seguro para la contraseÃ±a en texto plano.
    bcrypt.gensalt() genera un salt aleatorio de 12 rondas por defecto.
    """
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


# â”€â”€ GestiÃ³n de usuarios (HU-08 - Sprint 2) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def listar_usuarios() -> list[dict]:
    """
    Retorna todos los usuarios del sistema con su rol.
    Usado en la pantalla de gestiÃ³n de usuarios (solo Gerencia).
    """
    with db_cursor() as cur:
        # JOIN para traer el nombre del rol en lugar del ID
        cur.execute("""
            SELECT u.id, u.cedula, u.nombre, u.username,
                   r.nombre AS rol, u.activo, u.bloqueado,
                   u.creado_en
            FROM usuarios u
            JOIN roles r ON r.id = u.rol_id
            ORDER BY u.nombre  -- Orden alfabÃ©tico para la tabla de la UI
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
        # Generamos el hash de la contraseÃ±a antes de guardar
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
        # ViolaciÃ³n UNIQUE indica que ya existe cÃ©dula o username
        if "unique" in str(e).lower():
            return False, "Ya existe un usuario con esa cÃ©dula o nombre de usuario."
        return False, f"Error: {e}"


def editar_usuario(uid: int, nombre: str, rol_nombre: str,
                   activo: bool, nueva_clave: str = "") -> tuple[bool, str]:
    """
    Actualiza los datos de un usuario existente.
    Si nueva_clave es una cadena no vacÃ­a, tambiÃ©n cambia la contraseÃ±a.
    Retorna (exito: bool, mensaje: str).
    """
    try:
        with db_cursor(commit=True) as cur:
            # Obtenemos el ID del nuevo rol
            cur.execute("SELECT id FROM roles WHERE nombre = %s", (rol_nombre,))
            rol = cur.fetchone()
            if not rol:
                return False, f"Rol '{rol_nombre}' no encontrado."

            if nueva_clave.strip():
                # Si se proporcionÃ³ nueva contraseÃ±a, la incluimos en el UPDATE
                ph = hash_password(nueva_clave)
                cur.execute("""
                    UPDATE usuarios
                    SET nombre=%s, rol_id=%s, activo=%s, password_hash=%s,
                        bloqueado=FALSE, intentos_fallidos=0
                    WHERE id=%s
                """, (nombre.strip(), rol["id"], activo, ph, uid))
            else:
                # Sin nueva contraseÃ±a, solo actualizamos los demÃ¡s campos
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
    Ãštil cuando el administrador quiere rehabilitar una cuenta bloqueada.
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

