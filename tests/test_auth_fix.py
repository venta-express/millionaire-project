"""Tests adicionales para models/auth.py - fix variables no usadas"""
import pytest
from unittest.mock import patch, MagicMock
from models.auth import hash_password, Usuario


def test_hash_password_verifica_correcto():
    import bcrypt
    plain = "test_password_123"
    hashed = hash_password(plain)
    assert bcrypt.checkpw(plain.encode(), hashed.encode())


def test_crear_usuario_rol_no_existe():
    from models.auth import crear_usuario
    with patch("models.auth.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = None
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _ = crear_usuario("123", "Juan", "juan", "pass", "RolInexistente")
        assert ok is False


def test_editar_usuario_mock():
    from models.auth import editar_usuario
    mock_rol = {"id": 1}
    with patch("models.auth.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = mock_rol
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _ = editar_usuario(1, "Juan", "Gerencia", True)
        assert ok is True


def test_editar_usuario_con_nueva_password():
    from models.auth import editar_usuario
    mock_rol = {"id": 1}
    with patch("models.auth.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = mock_rol
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _ = editar_usuario(1, "Juan", "Gerencia", True, "nueva_pass")
        assert ok is True


def test_editar_usuario_rol_no_existe():
    from models.auth import editar_usuario
    with patch("models.auth.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = None
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _ = editar_usuario(1, "Juan", "RolInexistente", True)
        assert ok is False

