"""Tests completos para models/ventas.py"""
import pytest
from unittest.mock import patch, MagicMock
from models.ventas import ItemVenta, Cliente


def test_item_venta_subtotal_calculado():
    item = ItemVenta(1, "P001", "Prod", 10000.0, 3)
    assert item.subtotal == pytest.approx(30000.0)


def test_item_venta_subtotal_decimal():
    item = ItemVenta(1, "P001", "Prod", 15000.5, 2)
    assert item.subtotal == pytest.approx(31001.0)


def test_cliente_creacion():
    c = Cliente(1, "123456789", "Juan Perez", "3001234567", "j@mail.com")
    assert c.id == 1
    assert c.cedula == "123456789"


def test_crear_venta_sin_items():
    from models.ventas import crear_venta
    ok, msg = crear_venta(1, 1, [], "Efectivo", 0)
    assert ok is False


def test_registrar_venta_sin_items():
    from models.ventas import registrar_venta
    ok, msg, vid = registrar_venta(1, 1, [], "Efectivo")
    assert ok is False
    assert vid is None


def test_registrar_venta_metodo_invalido():
    from models.ventas import registrar_venta
    item = ItemVenta(1, "P001", "Prod", 10000.0, 1)
    ok, msg, vid = registrar_venta(1, 1, [item], "Cheque")
    assert ok is False


def test_registrar_venta_transferencia_sin_referencia():
    from models.ventas import registrar_venta
    item = ItemVenta(1, "P001", "Prod", 10000.0, 1)
    ok, msg, vid = registrar_venta(1, 1, [item], "Transferencia", "")
    assert ok is False


def test_buscar_clientes_mock():
    from models.ventas import buscar_clientes
    with patch("models.ventas.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        resultado = buscar_clientes("juan")
        assert isinstance(resultado, list)


def test_obtener_o_crear_cliente_cedula_vacia():
    from models.ventas import obtener_o_crear_cliente
    ok, msg, cid = obtener_o_crear_cliente("", "Juan")
    assert ok is False
    assert cid is None


def test_obtener_o_crear_cliente_nombre_vacio():
    from models.ventas import obtener_o_crear_cliente
    ok, msg, cid = obtener_o_crear_cliente("123456789", "")
    assert ok is False


def test_buscar_cliente_por_cedula_no_existe():
    from models.ventas import buscar_cliente_por_cedula
    with patch("models.ventas.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = None
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        resultado = buscar_cliente_por_cedula("000")
        assert resultado is None


def test_historial_cliente_mock():
    from models.ventas import historial_cliente
    with patch("models.ventas.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        resultado = historial_cliente(1)
        assert isinstance(resultado, list)


def test_listar_ventas_mock():
    from models.ventas import listar_ventas
    with patch("models.ventas.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        resultado = listar_ventas()
        assert isinstance(resultado, list)

