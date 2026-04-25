"""
Tests unitarios para models/promociones.py
Sprint 4: Firma correcta de crear_promocion, pytest.approx para floats,
          fechas validas respecto a hoy.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
from models.promociones import (
    Promocion,
    crear_promocion, listar_promociones, calcular_descuento,
    activar_desactivar_promocion, eliminar_promocion,
)

# Fechas que siempre seran validas (futuras)
HOY = date.today()
INICIO = HOY
FIN = HOY + timedelta(days=90)


def _make_ctx(cur=None):
    if cur is None:
        cur = MagicMock()
    ctx = MagicMock()
    ctx.return_value.__enter__ = MagicMock(return_value=cur)
    ctx.return_value.__exit__ = MagicMock(return_value=False)
    return cur, ctx


# â”€â”€ Tests dataclass â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_promocion_creacion():
    p = Promocion(1, "Desc verano", "porcentaje", 10.0,
                  1, None, HOY, FIN, True)
    assert p.nombre == "Desc verano"
    assert p.tipo_descuento == "porcentaje"
    assert p.activa is True


def test_promocion_valor_fijo():
    p = Promocion(1, "Promo fija", "valor_fijo", 5000.0,
                  None, 1, HOY, FIN, True)
    assert p.tipo_descuento == "valor_fijo"


def test_promocion_inactiva():
    p = Promocion(1, "Promo", "porcentaje", 5.0,
                  1, None, HOY, FIN, False)
    assert p.activa is False


# â”€â”€ Tests crear_promocion â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_crear_tipo_invalido():
    ok, _ = crear_promocion("P", "malo", 10.0, 1, None, INICIO, FIN, 1)
    assert ok is False


def test_crear_valor_cero():
    ok, _ = crear_promocion("P", "porcentaje", 0.0, 1, None, INICIO, FIN, 1)
    assert ok is False


def test_crear_valor_negativo():
    ok, _ = crear_promocion("P", "porcentaje", -5.0, 1, None, INICIO, FIN, 1)
    assert ok is False


def test_crear_fechas_invertidas():
    ok, _ = crear_promocion("P", "porcentaje", 10.0, 1, None, FIN, INICIO, 1)
    assert ok is False


def test_crear_sin_objetivo():
    ok, _ = crear_promocion("P", "porcentaje", 10.0, None, None, INICIO, FIN, 1)
    assert ok is False


def test_crear_ambos_objetivos():
    ok, _ = crear_promocion("P", "porcentaje", 10.0, 1, 2, INICIO, FIN, 1)
    assert ok is False


def test_crear_nombre_vacio():
    ok, _ = crear_promocion("", "porcentaje", 10.0, 1, None, INICIO, FIN, 1)
    assert ok is False


def test_crear_exitosa_producto():
    _, ctx = _make_ctx()
    with patch("models.promociones.db_cursor", ctx):
        ok, _ = crear_promocion("Promo", "porcentaje", 10.0, 1, None, INICIO, FIN, 1)
        assert ok is True


def test_crear_exitosa_categoria():
    _, ctx = _make_ctx()
    with patch("models.promociones.db_cursor", ctx):
        ok, _ = crear_promocion("Promo cat", "valor_fijo", 5000.0, None, 2, INICIO, FIN, 1)
        assert ok is True


def test_crear_error_bd():
    ctx = MagicMock()
    ctx.side_effect = Exception("Error BD")
    with patch("models.promociones.db_cursor", ctx):
        ok, _ = crear_promocion("Promo", "porcentaje", 10.0, 1, None, INICIO, FIN, 1)
        assert ok is False


# â”€â”€ Tests listar_promociones â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_listar_todas():
    _, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.promociones.db_cursor", ctx):
        assert isinstance(listar_promociones(), list)


def test_listar_activas():
    _, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.promociones.db_cursor", ctx):
        assert isinstance(listar_promociones(solo_activas=True), list)


# â”€â”€ Tests calcular_descuento â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_calcular_sin_promo():
    _, ctx = _make_ctx()
    cur.fetchone.return_value = None
    with patch("models.promociones.db_cursor", ctx):
        d, n = calcular_descuento(1, 50000.0)
        assert d == pytest.approx(0.0)
        assert n == ""


def test_calcular_porcentaje():
    _, ctx = _make_ctx()
    cur.fetchone.return_value = {
        "nombre": "D10", "tipo_descuento": "porcentaje", "valor": 10.0
    }
    with patch("models.promociones.db_cursor", ctx):
        d, n = calcular_descuento(1, 100000.0)
        assert d == pytest.approx(10000.0)
        assert n == "D10"


def test_calcular_valor_fijo():
    _, ctx = _make_ctx()
    cur.fetchone.return_value = {
        "nombre": "D5k", "tipo_descuento": "valor_fijo", "valor": 5000.0
    }
    with patch("models.promociones.db_cursor", ctx):
        d, _ = calcular_descuento(1, 100000.0)
        assert d == pytest.approx(5000.0)


def test_calcular_porcentaje_50k():
    _, ctx = _make_ctx()
    cur.fetchone.return_value = {
        "nombre": "D10", "tipo_descuento": "porcentaje", "valor": 10.0
    }
    with patch("models.promociones.db_cursor", ctx):
        d, _ = calcular_descuento(1, 50000.0)
        assert d == pytest.approx(5000.0)


# â”€â”€ Tests activar/desactivar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_activar():
    _, ctx = _make_ctx()
    with patch("models.promociones.db_cursor", ctx):
        ok, _ = activar_desactivar_promocion(1, True)
        assert ok is True
        assert "activada" in msg


def test_desactivar():
    _, ctx = _make_ctx()
    with patch("models.promociones.db_cursor", ctx):
        ok, _ = activar_desactivar_promocion(1, False)
        assert ok is True
        assert "desactivada" in msg


# â”€â”€ Tests eliminar_promocion â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_eliminar_ok():
    _, ctx = _make_ctx()
    with patch("models.promociones.db_cursor", ctx):
        ok, _ = eliminar_promocion(1)
        assert ok is True


def test_eliminar_falla():
    ctx = MagicMock()
    ctx.side_effect = Exception("Error BD")
    with patch("models.promociones.db_cursor", ctx):
        ok, _ = eliminar_promocion(1)
        assert ok is False


