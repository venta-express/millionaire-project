"""
Tests unitarios para models/ventas.py
Sprint 4: Cobertura de logica de ventas.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


def test_generar_numero_factura_formato():
    """El numero de factura debe tener formato correcto."""
    with patch("models.ventas.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = {"max_num": None}
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.ventas import generar_numero_factura
        numero = generar_numero_factura()
        assert isinstance(numero, str)
        assert len(numero) > 0


def test_crear_venta_datos_invalidos():
    """crear_venta debe fallar si no hay items."""
    from models.ventas import crear_venta
    ok, msg = crear_venta(
        cliente_id=1, vendedor_id=1,
        items=[], metodo_pago="Efectivo",
        descuento_global=0
    )
    assert ok is False


def test_listar_ventas_mock():
    """listar_ventas debe retornar lista de ventas."""
    mock_rows = [{
        "id": 1, "numero_factura": "FAC-001",
        "cliente_nombre": "Juan", "vendedor_nombre": "Admin",
        "fecha_hora": datetime.now(), "total": 50000.0,
        "metodo_pago": "Efectivo", "estado": "Completada"
    }]
    with patch("models.ventas.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = mock_rows
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.ventas import listar_ventas
        resultado = listar_ventas()
        assert isinstance(resultado, list)


def test_obtener_detalle_venta_mock():
    """obtener_detalle_venta debe retornar lista de items."""
    with patch("models.ventas.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.ventas import obtener_detalle_venta
        resultado = obtener_detalle_venta(1)
        assert isinstance(resultado, list)
