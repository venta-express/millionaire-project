"""Tests completos para models/auth.py - aumentar cobertura"""
import pytest
from unittest.mock import patch, MagicMock, call
from models.auth import (
    Usuario, get_usuario_activo, set_usuario_activo,
    cerrar_sesion, hash_password, MAX_INTENTOS
)


def test_hash_password_genera_hash():
    h = hash_password("mi_password_123")
    assert h.startswith("$2b$")
    assert len(h) > 30


def test_hash_password_diferente_cada_vez():
    h1 = hash_password("password")
    h2 = hash_password("password")
    assert h1 != h2


def test_iniciar_sesion_campos_vacios():
    from models.auth import iniciar_sesion
    ok, _, u = iniciar_sesion("", "")
    assert ok is False
    assert u is None


def test_iniciar_sesion_username_vacio():
    from models.auth import iniciar_sesion
    ok, _, u = iniciar_sesion("", "password")
    assert ok is False


def test_iniciar_sesion_password_vacio():
    from models.auth import iniciar_sesion
    ok, _, u = iniciar_sesion("admin", "")
    assert ok is False


def test_iniciar_sesion_usuario_no_existe():
    from models.auth import iniciar_sesion
    with patch("models.auth.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = None
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _, u = iniciar_sesion("noexiste", "pass")
        assert ok is False
        assert u is None


def test_iniciar_sesion_cuenta_bloqueada():
    from models.auth import iniciar_sesion
    mock_row = {
        "id": 1, "cedula": "123", "nombre": "Juan", "username": "juan",
        "hash_acceso": "pw_hash_mock", "activo": True, "bloqueado": True,
        "intentos_fallidos": 3, "rol": "Vendedor"
    }
    with patch("models.auth.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = mock_row
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _, u = iniciar_sesion("juan", "pass")
        assert ok is False
        assert "bloqueada" in msg.lower()


def test_iniciar_sesion_cuenta_inactiva():
    from models.auth import iniciar_sesion
    mock_row = {
        "id": 1, "cedula": "123", "nombre": "Juan", "username": "juan",
        "hash_acceso": "pw_hash_mock", "activo": False, "bloqueado": False,
        "intentos_fallidos": 0, "rol": "Vendedor"
    }
    with patch("models.auth.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = mock_row
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _, u = iniciar_sesion("juan", "pass")
        assert ok is False
        assert "inactiva" in msg.lower()


def test_crear_usuario_campos_vacios():
    from models.auth import crear_usuario
    with patch("models.auth.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = None
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _ = crear_usuario("", "Juan", "juan", "pass", "Vendedor")
        assert ok is False


def test_listar_roles_mock():
    from models.auth import listar_roles
    mock_rows = [{"nombre": "Gerencia"}, {"nombre": "Vendedor"}]
    with patch("models.auth.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = mock_rows
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        roles = listar_roles()
        assert isinstance(roles, list)
        assert "Gerencia" in roles


def test_desbloquear_usuario_mock():
    from models.auth import desbloquear_usuario
    with patch("models.auth.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _ = desbloquear_usuario(1)
        assert ok is True




