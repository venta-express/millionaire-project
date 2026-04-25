"""Tests completos para models/compras.py"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime, timedelta


def test_registrar_proveedor_exitoso():
    from models.compras import registrar_proveedor
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _ = registrar_proveedor("RepCo", "Juan", "3001234567", "j@r.com", "900-1")
        assert ok is True


def test_registrar_pedido_sin_items():
    from models.compras import registrar_pedido
    ok, _, pid = registrar_pedido(1, 1, date.today() + timedelta(days=5), [])
    assert ok is False
    assert pid is None


def test_registrar_pedido_fecha_pasada():
    from models.compras import registrar_pedido
    ok, _, pid = registrar_pedido(1, 1, date(2020, 1, 1), [{"producto_id": 1, "cantidad": 5}])
    assert ok is False
    assert pid is None


def test_listar_pedidos_con_estado_mock():
    from models.compras import listar_pedidos
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        resultado = listar_pedidos(estado="Pendiente")
        assert isinstance(resultado, list)


def test_actualizar_estado_pedido_invalido():
    from models.compras import actualizar_estado_pedido
    ok, _ = actualizar_estado_pedido(1, "EstadoInvalido")
    assert ok is False


def test_actualizar_estado_pedido_valido():
    from models.compras import actualizar_estado_pedido
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _ = actualizar_estado_pedido(1, "Cancelado")
        assert ok is True


def test_pedidos_pendientes_vencidos_mock():
    from models.compras import pedidos_pendientes_vencidos
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        resultado = pedidos_pendientes_vencidos()
        assert isinstance(resultado, list)


def test_actualizar_proveedor_nombre_vacio():
    from models.compras import actualizar_proveedor
    ok, _ = actualizar_proveedor(1, "", "Juan", "300", "j@r.com")
    assert ok is False


def test_actualizar_proveedor_exitoso():
    from models.compras import actualizar_proveedor
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _ = actualizar_proveedor(1, "RepCo", "Juan", "300", "j@r.com")
        assert ok is True


def test_desactivar_proveedor_mock():
    from models.compras import desactivar_proveedor
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _ = desactivar_proveedor(1)
        assert ok is True

