"""
Tests unitarios para models/auth.py
Sprint 4: Cobertura de autenticacion y gestion de usuarios.
"""

import pytest
from unittest.mock import patch, MagicMock
from models.auth import (
    Usuario, get_usuario_activo, set_usuario_activo,
    cerrar_sesion, MAX_INTENTOS,
    hash_password, iniciar_sesion, crear_usuario,
    editar_usuario, desbloquear_usuario, listar_usuarios, listar_roles,
)


def _make_ctx(cur=None):
    if cur is None:
        cur = MagicMock()
    ctx = MagicMock()
    ctx.return_value.__enter__ = MagicMock(return_value=cur)
    ctx.return_value.__exit__ = MagicMock(return_value=False)
    return cur, ctx


# â”€â”€ Tests de Usuario dataclass â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_usuario_creacion():
    u = Usuario(
        id=1, cedula="123456789", nombre="Juan Perez",
        username="juan", rol="Gerencia",
        activo=True, bloqueado=False
    )
    assert u.id == 1
    assert u.cedula == "123456789"
    assert u.nombre == "Juan Perez"
    assert u.username == "juan"
    assert u.rol == "Gerencia"
    assert u.activo is True
    assert u.bloqueado is False


def test_usuario_igualdad():
    u1 = Usuario(1, "123", "Juan", "juan", "Gerencia", True, False)
    u2 = Usuario(1, "123", "Juan", "juan", "Gerencia", True, False)
    assert u1 == u2


def test_usuario_diferente():
    u1 = Usuario(1, "123", "Juan", "juan", "Gerencia", True, False)
    u2 = Usuario(2, "456", "Pedro", "pedro", "Vendedor", True, False)
    assert u1 != u2


# â”€â”€ Tests de sesion global â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_sesion_inicialmente_none():
    set_usuario_activo(None)
    assert get_usuario_activo() is None


def test_set_y_get_usuario_activo():
    u = Usuario(1, "123", "Juan", "juan", "Gerencia", True, False)
    set_usuario_activo(u)
    assert get_usuario_activo() == u
    set_usuario_activo(None)


def test_cerrar_sesion():
    u = Usuario(1, "123", "Juan", "juan", "Gerencia", True, False)
    set_usuario_activo(u)
    cerrar_sesion()
    assert get_usuario_activo() is None


def test_max_intentos_es_3():
    assert MAX_INTENTOS == 3


# â”€â”€ Tests de roles â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_usuario_rol_gerencia():
    u = Usuario(1, "1", "Admin", "admin", "Gerencia", True, False)
    assert u.rol == "Gerencia"


def test_usuario_rol_vendedor():
    u = Usuario(2, "2", "Vendor", "vendor", "Vendedor", True, False)
    assert u.rol == "Vendedor"


def test_usuario_rol_inventario():
    u = Usuario(3, "3", "Inv", "inv", "Inventario", True, False)
    assert u.rol == "Inventario"


def test_usuario_bloqueado():
    u = Usuario(4, "4", "Bloq", "bloq", "Vendedor", True, True)
    assert u.bloqueado is True


def test_usuario_inactivo():
    u = Usuario(5, "5", "Inact", "inact", "Vendedor", False, False)
    assert u.activo is False


# â”€â”€ Tests hash_password â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_hash_retorna_string():
    resultado = hash_password("mi_clave_segura")
    assert isinstance(resultado, str)
    assert len(resultado) > 0


def test_hash_difiere_del_original():
    resultado = hash_password("mi_clave_segura")
    assert resultado != "mi_clave_segura"


def test_hash_bcrypt_verificable():
    import bcrypt
    clave = "clave_de_prueba_123"
    hashed = hash_password(clave)
    assert bcrypt.checkpw(clave.encode(), hashed.encode())


# â”€â”€ Tests iniciar_sesion â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_iniciar_sesion_campos_vacios():
    ok, msg, u = iniciar_sesion("", "")
    assert ok is False
    assert u is None


def test_iniciar_sesion_usuario_vacio():
    ok, msg, u = iniciar_sesion("", "clave123")
    assert ok is False
    assert u is None


def test_iniciar_sesion_clave_vacia():
    ok, msg, u = iniciar_sesion("admin", "")
    assert ok is False
    assert u is None


def test_iniciar_sesion_usuario_no_existe():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = None
    with patch("models.auth.db_cursor", ctx):
        ok, msg, u = iniciar_sesion("noexiste", "abc")
        assert ok is False
        assert u is None


def test_iniciar_sesion_bloqueada():
    """Cuenta bloqueada: se verifica el flag ANTES del checkpw para evitar
    ValueError con hashes invalidos en el mock."""
    # Hash estatico generado previamente; no es una credencial real
    _HASH_TEST = r"$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iKBi"
    mock_row = {
        "id": 1, "cedula": "1", "nombre": "Juan", "username": "juan",
        "password_hash": _HASH_TEST,
        "activo": True, "bloqueado": True,
        "intentos_fallidos": 3, "rol": "Vendedor",
    }
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = mock_row
    with patch("models.auth.db_cursor", ctx):
        ok, msg, u = iniciar_sesion("juan", "cualquier")
        assert ok is False
        assert "bloqueada" in msg.lower()


def test_iniciar_sesion_inactiva():
    """Cuenta inactiva: mismo patron con hash valido."""
    import bcrypt
    hash_valido = "mock_hash_no_es_credencial_real"
    mock_row = {
        "id": 1, "cedula": "1", "nombre": "Juan", "username": "juan",
        "password_hash": hash_valido,
        "activo": False, "bloqueado": False,
        "intentos_fallidos": 0, "rol": "Vendedor",
    }
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = mock_row
    with patch("models.auth.db_cursor", ctx):
        ok, msg, u = iniciar_sesion("juan", "cualquier")
        assert ok is False
        assert "inactiva" in msg.lower()


# â”€â”€ Tests crear_usuario â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_crear_usuario_exitoso():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = {"id": 2}
    with patch("models.auth.db_cursor", ctx):
        ok, _ = crear_usuario("123", "Juan", "juan", "clave_segura", "Vendedor")
        assert ok is True


def test_crear_usuario_rol_inexistente():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = None
    with patch("models.auth.db_cursor", ctx):
        ok, _ = crear_usuario("123", "Juan", "juan", "clave_segura", "RolInexistente")
        assert ok is False


def test_crear_usuario_duplicado():
    ctx = MagicMock()
    ctx.side_effect = Exception("unique constraint")
    with patch("models.auth.db_cursor", ctx):
        ok, msg = crear_usuario("123", "Juan", "juan", "clave_segura", "Vendedor")
        assert ok is False
        # El mensaje puede venir del modelo o del except; solo validamos que falle
        assert isinstance(msg, str)


# â”€â”€ Tests editar_usuario â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_editar_usuario_exitoso():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = {"id": 2}
    with patch("models.auth.db_cursor", ctx):
        ok, _ = editar_usuario(1, "Nuevo Nombre", "Vendedor", True)
        assert ok is True


def test_editar_usuario_nueva_clave():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = {"id": 2}
    with patch("models.auth.db_cursor", ctx):
        ok, _ = editar_usuario(1, "Nombre", "Vendedor", True, nueva_clave="clave_nueva_ok")
        assert ok is True


def test_editar_usuario_rol_inexistente():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = None
    with patch("models.auth.db_cursor", ctx):
        ok, _ = editar_usuario(1, "Nombre", "RolMalo", True)
        assert ok is False


# â”€â”€ Tests desbloquear_usuario â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_desbloquear_usuario():
    cur, ctx = _make_ctx()
    with patch("models.auth.db_cursor", ctx):
        ok, _ = desbloquear_usuario(1)
        assert ok is True


# â”€â”€ Tests listar_usuarios â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_listar_usuarios_mock():
    mock_row = {
        "id": 1, "cedula": "123", "nombre": "Juan",
        "username": "juan", "rol": "Gerencia",
        "activo": True, "bloqueado": False,
    }
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = [mock_row]
    with patch("models.auth.db_cursor", ctx):
        resultado = listar_usuarios()
        assert isinstance(resultado, list)


# â”€â”€ Tests listar_roles â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_listar_roles_mock():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = [{"nombre": "Gerencia"}, {"nombre": "Vendedor"}]
    with patch("models.auth.db_cursor", ctx):
        roles = listar_roles()
        assert isinstance(roles, list)
        assert "Gerencia" in roles







