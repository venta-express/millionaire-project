"""
Tests unitarios para models/promociones.py - CORREGIDO
Sprint 4: Firma correcta de crear_promocion, pytest.approx para floats.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from models.promociones import Promocion


def test_promocion_creacion():
    p = Promocion(1, "Desc verano", "porcentaje", 10.0,
                  1, None, date(2026,1,1), date(2026,12,31), True)
    assert p.nombre == "Desc verano"
    assert p.tipo_descuento == "porcentaje"
    assert p.activa is True


def test_promocion_valor_fijo():
    p = Promocion(1, "Promo fija", "valor_fijo", 5000.0,
                  None, 1, date.today(), date.today(), True)
    assert p.tipo_descuento == "valor_fijo"


def test_promocion_inactiva():
    p = Promocion(1, "Promo", "porcentaje", 5.0,
                  1, None, date.today(), date.today(), False)
    assert p.activa is False


# crear_promocion(nombre, tipo_descuento, valor, producto_id,
#                 categoria_id, fecha_inicio, fecha_fin, creado_por)

def test_crear_tipo_invalido():
    from models.promociones import crear_promocion
    ok, _ = crear_promocion("P", "malo", 10.0, 1, None, date.today(), date.today(), 1)
    assert ok is False

def test_crear_valor_cero():
    from models.promociones import crear_promocion
    ok, _ = crear_promocion("P", "porcentaje", 0.0, 1, None, date.today(), date.today(), 1)
    assert ok is False

def test_crear_valor_negativo():
    from models.promociones import crear_promocion
    ok, _ = crear_promocion("P", "porcentaje", -5.0, 1, None, date.today(), date.today(), 1)
    assert ok is False

def test_crear_fechas_invertidas():
    from models.promociones import crear_promocion
    ok, _ = crear_promocion("P", "porcentaje", 10.0, 1, None,
                             date(2026,12,31), date(2026,1,1), 1)
    assert ok is False

def test_crear_sin_objetivo():
    from models.promociones import crear_promocion
    ok, _ = crear_promocion("P", "porcentaje", 10.0, None, None,
                             date.today(), date.today(), 1)
    assert ok is False

def test_crear_ambos_objetivos():
    from models.promociones import crear_promocion
    ok, _ = crear_promocion("P", "porcentaje", 10.0, 1, 2,
                             date.today(), date.today(), 1)
    assert ok is False

def test_crear_nombre_vacio():
    from models.promociones import crear_promocion
    ok, _ = crear_promocion("", "porcentaje", 10.0, 1, None,
                             date.today(), date.today(), 1)
    assert ok is False

def test_crear_exitosa_producto():
    with patch("models.promociones.db_cursor") as mc:
        cur = MagicMock()
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.promociones import crear_promocion
        ok, _ = crear_promocion("Promo", "porcentaje", 10.0, 1, None,
                                 date(2026,1,1), date(2026,12,31), 1)
        assert ok is True

def test_crear_exitosa_categoria():
    with patch("models.promociones.db_cursor") as mc:
        cur = MagicMock()
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.promociones import crear_promocion
        ok, _ = crear_promocion("Promo cat", "valor_fijo", 5000.0, None, 2,
                                 date(2026,1,1), date(2026,12,31), 1)
        assert ok is True

def test_crear_error_bd():
    with patch("models.promociones.db_cursor") as mc:
        mc.side_effect = Exception("Error BD")
        from models.promociones import crear_promocion
        ok, _ = crear_promocion("Promo", "porcentaje", 10.0, 1, None,
                                 date.today(), date.today(), 1)
        assert ok is False


def test_listar_todas():
    with patch("models.promociones.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchall.return_value = []
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.promociones import listar_promociones
        assert isinstance(listar_promociones(), list)

def test_listar_activas():
    with patch("models.promociones.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchall.return_value = []
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.promociones import listar_promociones
        assert isinstance(listar_promociones(solo_activas=True), list)


def test_calcular_sin_promo():
    with patch("models.promociones.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchone.return_value = None
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.promociones import calcular_descuento
        d, n = calcular_descuento(1, 50000.0)
        assert d == pytest.approx(0.0)
        assert n == ""

def test_calcular_porcentaje():
    with patch("models.promociones.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchone.return_value = {"nombre": "D10", "tipo_descuento": "porcentaje", "valor": 10.0}
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.promociones import calcular_descuento
        d, n = calcular_descuento(1, 100000.0)
        assert d == pytest.approx(10000.0)
        assert n == "D10"

def test_calcular_valor_fijo():
    with patch("models.promociones.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchone.return_value = {"nombre": "D5k", "tipo_descuento": "valor_fijo", "valor": 5000.0}
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.promociones import calcular_descuento
        d, _ = calcular_descuento(1, 100000.0)
        assert d == pytest.approx(5000.0)

def test_calcular_porcentaje_50k():
    with patch("models.promociones.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchone.return_value = {"nombre": "D10", "tipo_descuento": "porcentaje", "valor": 10.0}
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.promociones import calcular_descuento
        d, _ = calcular_descuento(1, 50000.0)
        assert d == pytest.approx(5000.0)


def test_activar():
    with patch("models.promociones.db_cursor") as mc:
        cur = MagicMock()
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.promociones import activar_desactivar_promocion
        ok, msg = activar_desactivar_promocion(1, True)
        assert ok is True
        assert "activada" in msg

def test_desactivar():
    with patch("models.promociones.db_cursor") as mc:
        cur = MagicMock()
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.promociones import activar_desactivar_promocion
        ok, msg = activar_desactivar_promocion(1, False)
        assert ok is True
        assert "desactivada" in msg

def test_eliminar_ok():
    with patch("models.promociones.db_cursor") as mc:
        cur = MagicMock()
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.promociones import eliminar_promocion
        ok, _ = eliminar_promocion(1)
        assert ok is True

def test_eliminar_falla():
    with patch("models.promociones.db_cursor") as mc:
        mc.side_effect = Exception("Error BD")
        from models.promociones import eliminar_promocion
        ok, _ = eliminar_promocion(1)
        assert ok is False
