"""
Tests unitarios para models/auth.py
Sprint 4: Cobertura de autenticacion y gestion de usuarios.
"""

import pytest
from unittest.mock import patch, MagicMock
from models.auth import (
    Usuario, get_usuario_activo, set_usuario_activo,
    cerrar_sesion, MAX_INTENTOS
)


# ── Tests de Usuario dataclass ────────────────────────────────────────────────

def test_usuario_creacion():
    """Verifica que se puede crear un Usuario con todos sus campos."""
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
    """Dos usuarios con los mismos datos deben ser iguales."""
    u1 = Usuario(1, "123", "Juan", "juan", "Gerencia", True, False)
    u2 = Usuario(1, "123", "Juan", "juan", "Gerencia", True, False)
    assert u1 == u2


def test_usuario_diferente():
    """Dos usuarios con diferente ID deben ser distintos."""
    u1 = Usuario(1, "123", "Juan", "juan", "Gerencia", True, False)
    u2 = Usuario(2, "456", "Pedro", "pedro", "Vendedor", True, False)
    assert u1 != u2


# ── Tests de sesion global ────────────────────────────────────────────────────

def test_sesion_inicialmente_none():
    """Al inicio no debe haber sesion activa."""
    set_usuario_activo(None)
    assert get_usuario_activo() is None


def test_set_y_get_usuario_activo():
    """set_usuario_activo debe actualizar la sesion global."""
    u = Usuario(1, "123", "Juan", "juan", "Gerencia", True, False)
    set_usuario_activo(u)
    assert get_usuario_activo() == u
    set_usuario_activo(None)


def test_cerrar_sesion():
    """cerrar_sesion debe dejar la sesion en None."""
    u = Usuario(1, "123", "Juan", "juan", "Gerencia", True, False)
    set_usuario_activo(u)
    cerrar_sesion()
    assert get_usuario_activo() is None


def test_max_intentos_es_3():
    """La constante MAX_INTENTOS debe ser 3."""
    assert MAX_INTENTOS == 3


# ── Tests de roles ────────────────────────────────────────────────────────────

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


# ── Tests con mock de BD ──────────────────────────────────────────────────────

def test_listar_usuarios_mock():
    """listar_usuarios debe retornar lista de dicts desde la BD."""
    from unittest.mock import patch, MagicMock
    mock_row = {
        "id": 1, "cedula": "123", "nombre": "Juan",
        "username": "juan", "rol": "Gerencia",
        "activo": True, "bloqueado": False
    }
    with patch("models.auth.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [mock_row]
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.auth import listar_usuarios
        resultado = listar_usuarios()
        assert isinstance(resultado, list)
