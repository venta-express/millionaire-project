"""
Tests unitarios para models/ventas.py
Sprint 4: Cobertura de logica de ventas.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from models.ventas import (
    generar_numero_factura,
    registrar_venta,
    obtener_venta,
    historial_cliente,
    buscar_clientes,
    buscar_cliente_por_cedula,
    buscar_clientes_historial,
    obtener_o_crear_cliente,
    ItemVenta,
)


def _make_ctx(cur=None):
    if cur is None:
        cur = MagicMock()
    ctx = MagicMock()
    ctx.return_value.__enter__ = MagicMock(return_value=cur)
    ctx.return_value.__exit__ = MagicMock(return_value=False)
    return cur, ctx


def test_generar_numero_factura_formato():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = {"max_num": None}
    with patch("models.ventas.db_cursor", ctx):
        numero = generar_numero_factura()
        assert isinstance(numero, str)
        assert len(numero) > 0


def test_registrar_venta_sin_items():
    ok, msg, _ = registrar_venta(1, 1, [], "Efectivo")
    assert ok is False


def test_registrar_venta_metodo_invalido():
    item = ItemVenta(1, "P001", "Freno", 45000.0, 1)
    ok, msg, _ = registrar_venta(1, 1, [item], "Cheque")
    assert ok is False


def test_registrar_venta_transferencia_sin_ref():
    item = ItemVenta(1, "P001", "Freno", 45000.0, 1)
    ok, msg, _ = registrar_venta(1, 1, [item], "Transferencia", referencia_pago="")
    assert ok is False


def test_obtener_venta_mock():
    mock_row = {"id": 1, "numero_factura": "FAC-001", "cliente_id": 1,
                "vendedor_id": 1, "subtotal": 50000.0, "descuento": 0.0,
                "total": 50000.0, "metodo_pago": "Efectivo",
                "referencia_pago": "", "notas": "", "estado": "Completada",
                "fecha_hora": datetime.now()}
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = mock_row
    with patch("models.ventas.db_cursor", ctx):
        assert obtener_venta(1) is not None


def test_obtener_venta_no_existe():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = None
    with patch("models.ventas.db_cursor", ctx):
        assert obtener_venta(999) is None


def test_buscar_clientes_mock():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.ventas.db_cursor", ctx):
        assert isinstance(buscar_clientes("Juan"), list)


def test_buscar_cliente_cedula_existe():
    mock_row = {"id": 1, "cedula": "123", "nombre": "Juan",
                "telefono": "300", "email": "j@j.com"}
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = mock_row
    with patch("models.ventas.db_cursor", ctx):
        assert buscar_cliente_por_cedula("123") is not None


def test_buscar_cliente_cedula_no_existe():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = None
    with patch("models.ventas.db_cursor", ctx):
        assert buscar_cliente_por_cedula("999") is None


def test_historial_cliente_mock():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.ventas.db_cursor", ctx):
        assert isinstance(historial_cliente(1), list)


def test_buscar_clientes_historial_mock():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.ventas.db_cursor", ctx):
        assert isinstance(buscar_clientes_historial("Juan"), list)


def test_obtener_o_crear_cliente_existente():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = {"id": 1}
    with patch("models.ventas.db_cursor", ctx):
        ok, _, cid = obtener_o_crear_cliente("123456789", "Juan")
        assert ok is True
        assert cid == 1
