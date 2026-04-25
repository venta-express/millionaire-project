"""Tests adicionales para models/promociones.py - fix issues SonarCloud"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date


def test_crear_promocion_tipo_invalido():
    from models.promociones import crear_promocion
    ok, msg = crear_promocion("Promo", "invalido", 10.0, 1, None,
                               date.today(), date.today(), 1)
    assert ok is False


def test_crear_promocion_valor_cero():
    from models.promociones import crear_promocion
    ok, msg = crear_promocion("Promo", "porcentaje", 0.0, 1, None,
                               date.today(), date.today(), 1)
    assert ok is False


def test_crear_promocion_fecha_fin_antes_inicio():
    from models.promociones import crear_promocion
    ok, msg = crear_promocion("Promo", "porcentaje", 10.0, 1, None,
                               date(2026, 12, 31), date(2026, 1, 1), 1)
    assert ok is False


def test_crear_promocion_nombre_vacio():
    from models.promociones import crear_promocion
    ok, msg = crear_promocion("", "porcentaje", 10.0, 1, None,
                               date.today(), date.today(), 1)
    assert ok is False


def test_activar_promocion_mock():
    from models.promociones import activar_desactivar_promocion
    with patch("models.promociones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, msg = activar_desactivar_promocion(1, True)
        assert ok is True
        assert "activada" in msg


def test_desactivar_promocion_mock():
    from models.promociones import activar_desactivar_promocion
    with patch("models.promociones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, msg = activar_desactivar_promocion(1, False)
        assert ok is True
        assert "desactivada" in msg


def test_eliminar_promocion_mock():
    from models.promociones import eliminar_promocion
    with patch("models.promociones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, msg = eliminar_promocion(1)
        assert ok is True


def test_calcular_descuento_porcentaje():
    from models.promociones import calcular_descuento
    mock_row = {"nombre": "Desc10", "tipo_descuento": "porcentaje", "valor": 10.0}
    with patch("models.promociones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = mock_row
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        monto, nombre = calcular_descuento(1, 100000.0)
        assert monto == pytest.approx(10000.0)
        assert nombre == "Desc10"


def test_calcular_descuento_valor_fijo():
    from models.promociones import calcular_descuento
    mock_row = {"nombre": "Desc5k", "tipo_descuento": "valor_fijo", "valor": 5000.0}
    with patch("models.promociones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = mock_row
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        monto, nombre = calcular_descuento(1, 100000.0)
        assert monto == pytest.approx(5000.0)

