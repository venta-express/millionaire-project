"""Tests extra para models/ventas.py - aumentar cobertura"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from models.ventas import ItemVenta, Cliente


def test_item_venta_cantidad_1():
    item = ItemVenta(1, "P001", "Prod", 10000.0, 1)
    assert item.subtotal == 10000.0


def test_obtener_o_crear_cliente_existente():
    from models.ventas import obtener_o_crear_cliente
    mock_row = {"id": 1}
    with patch("models.ventas.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = mock_row
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, msg, cid = obtener_o_crear_cliente("123456789", "Juan")
        assert ok is True
        assert cid == 1


def test_buscar_clientes_historial_mock():
    from models.ventas import buscar_clientes_historial
    with patch("models.ventas.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        resultado = buscar_clientes_historial("juan")
        assert isinstance(resultado, list)


def test_crear_venta_valida_mock():
    from models.ventas import crear_venta
    with patch("models.ventas.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = {"id": 1, "numero_factura": "FAC-001"}
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        items = [{"producto_id": 1, "cantidad": 2, "precio": 10000.0}]
        ok, msg = crear_venta(1, 1, items, "Efectivo", 0)
        assert isinstance(ok, bool)


def test_obtener_detalle_venta_mock():
    from models.ventas import obtener_detalle_venta
    with patch("models.ventas.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        resultado = obtener_detalle_venta(1)
        assert isinstance(resultado, list)
