"""Tests unitarios para models/promociones.py"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from models.promociones import Promocion


def test_promocion_creacion():
    p = Promocion(
        id=1, nombre="Desc Frenos", tipo_descuento="porcentaje",
        valor=10.0, producto_id=1, categoria_id=None,
        fecha_inicio=date(2026, 1, 1), fecha_fin=date(2026, 12, 31), activa=True
    )
    assert p.nombre == "Desc Frenos"
    assert p.valor == 10.0
    assert p.activa is True

def test_promocion_tipo_porcentaje():
    p = Promocion(1, "P", "porcentaje", 15.0, 1, None,
                  date.today(), date.today(), True)
    assert p.tipo_descuento == "porcentaje"

def test_promocion_tipo_valor_fijo():
    p = Promocion(1, "P", "valor_fijo", 5000.0, None, 1,
                  date.today(), date.today(), True)
    assert p.tipo_descuento == "valor_fijo"

def test_promocion_inactiva():
    p = Promocion(1, "P", "porcentaje", 10.0, 1, None,
                  date.today(), date.today(), False)
    assert p.activa is False

def test_listar_promociones_mock():
    with patch("models.promociones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.promociones import listar_promociones
        assert isinstance(listar_promociones(), list)

def test_listar_promociones_activas_mock():
    with patch("models.promociones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.promociones import listar_promociones
        assert isinstance(listar_promociones(solo_activas=True), list)

def test_calcular_descuento_sin_promo():
    with patch("models.promociones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = None
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.promociones import calcular_descuento
        desc = calcular_descuento(producto_id=1, categoria_id=1, precio=10000.0)
        assert desc == 0.0
