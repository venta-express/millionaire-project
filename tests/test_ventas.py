"""
Tests unitarios para models/ventas.py
Sprint 4: Cobertura de logica de ventas.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from models.ventas import (
    generar_numero_factura,
    crear_venta, registrar_venta,
    listar_ventas, obtener_detalle_venta,
    ItemVenta,
)


def _make_ctx(cur=None):
    if cur is None:
        cur = MagicMock()
    ctx = MagicMock()
    ctx.return_value.__enter__ = MagicMock(return_value=cur)
    ctx.return_value.__exit__ = MagicMock(return_value=False)
    return cur, ctx


# ── generar_numero_factura ────────────────────────────────────────────────────

def test_generar_numero_factura_formato():
    """El numero de factura debe ser un string no vacio."""
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = {"max_num": None}
    with patch("models.ventas.db_cursor", ctx):
        numero = generar_numero_factura()
        assert isinstance(numero, str)
        assert len(numero) > 0


# ── crear_venta / registrar_venta ─────────────────────────────────────────────

def test_crear_venta_sin_items():
    """crear_venta debe fallar si no hay items.
    Acepta tanto (ok, msg) como (ok, msg, id) segun implementacion."""
    resultado = crear_venta(
        cliente_id=1, vendedor_id=1,
        items=[], metodo_pago="Efectivo",
        descuento_global=0,
    )
    ok = resultado[0]
    assert ok is False


def test_registrar_venta_sin_items():
    """registrar_venta tambien debe rechazar lista vacia."""
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


# ── listar_ventas ─────────────────────────────────────────────────────────────

def test_listar_ventas_mock():
    """listar_ventas debe retornar lista de ventas."""
    mock_rows = [{
        "id": 1, "numero_factura": "FAC-001",
        "cliente_nombre": "Juan", "vendedor_nombre": "Admin",
        "fecha_hora": datetime.now(), "total": 50000.0,
        "metodo_pago": "Efectivo", "estado": "Completada",
    }]
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = mock_rows
    with patch("models.ventas.db_cursor", ctx):
        resultado = listar_ventas()
        assert isinstance(resultado, list)


def test_listar_ventas_vacia():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.ventas.db_cursor", ctx):
        resultado = listar_ventas()
        assert resultado == []


# ── obtener_detalle_venta ─────────────────────────────────────────────────────

def test_obtener_detalle_venta_mock():
    """obtener_detalle_venta debe retornar lista de items."""
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.ventas.db_cursor", ctx):
        resultado = obtener_detalle_venta(1)
        assert isinstance(resultado, list)
