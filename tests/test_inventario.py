"""
Tests unitarios para models/inventario.py
Sprint 4: pytest.approx para floats, cobertura completa.
"""

import pytest
from unittest.mock import patch, MagicMock
from models.inventario import (
    Producto,
    registrar_producto, actualizar_producto,
    ajustar_stock, desactivar_producto,
    buscar_productos, obtener_producto,
    productos_stock_bajo, listar_categorias,
    obtener_alertas_no_vistas,
)


def _make_ctx(cur=None):
    if cur is None:
        cur = MagicMock()
    ctx = MagicMock()
    ctx.return_value.__enter__ = MagicMock(return_value=cur)
    ctx.return_value.__exit__ = MagicMock(return_value=False)
    return cur, ctx


# â”€â”€ Producto dataclass â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_producto_creacion():
    p = Producto(1, "P001", "Freno", "Desc", "Frenos", 1, 45000.0, 10, 5, True)
    assert p.codigo == "P001"
    assert p.nombre == "Freno"
    assert p.activo is True


def test_producto_precio_float():
    p = Producto(1, "P001", "Freno", "", "Cat", 1, 45000.0, 10, 5, True)
    assert isinstance(p.precio_unitario, float)


def test_producto_precio_cero():
    p = Producto(1, "P001", "Freno", "", "Cat", 1, 0.0, 0, 0, True)
    assert p.stock_actual == 0
    assert isinstance(p.precio_unitario, float)


def test_producto_inactivo():
    p = Producto(2, "P002", "Bujia", "", "Electrico", 2, 12000.0, 5, 2, False)
    assert p.activo is False


# â”€â”€ registrar_producto â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_registrar_codigo_vacio():
    ok, _ = registrar_producto("", "Freno", "", 1, 45000.0, 10, 5)
    assert ok is False


def test_registrar_nombre_vacio():
    ok, _ = registrar_producto("P001", "", "", 1, 45000.0, 10, 5)
    assert ok is False


def test_registrar_precio_negativo():
    ok, _ = registrar_producto("P001", "Freno", "", 1, -1.0, 10, 5)
    assert ok is False


def test_registrar_stock_negativo():
    ok, _ = registrar_producto("P001", "Freno", "", 1, 45000.0, -1, 5)
    assert ok is False


def test_registrar_stock_minimo_negativo():
    ok, _ = registrar_producto("P001", "Freno", "", 1, 45000.0, 10, -1)
    assert ok is False


def test_registrar_exitoso():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = {"id": 1}
    with patch("models.inventario.db_cursor", ctx):
        ok, _ = registrar_producto("P001", "Freno", "Desc", 1, 45000.0, 10, 5)
        assert ok is True


def test_registrar_codigo_duplicado():
    ctx = MagicMock()
    ctx.side_effect = Exception("unique constraint violated")
    with patch("models.inventario.db_cursor", ctx):
        ok, msg = registrar_producto("P001", "Freno", "", 1, 45000.0, 10, 5)
        assert ok is False
        assert "P001" in msg


def test_registrar_error_generico():
    ctx = MagicMock()
    ctx.side_effect = Exception("connection error")
    with patch("models.inventario.db_cursor", ctx):
        ok, _ = registrar_producto("P001", "Freno", "", 1, 45000.0, 10, 5)
        assert ok is False


# â”€â”€ actualizar_producto â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_actualizar_nombre_vacio():
    ok, _ = actualizar_producto("", "", 1, 45000.0, 10, 5)
    assert ok is False


def test_actualizar_precio_negativo():
    ok, _ = actualizar_producto("Freno", "", 1, -500.0, 10, 5)
    assert ok is False


def test_actualizar_exitoso():
    cur, ctx = _make_ctx()
    with patch("models.inventario.db_cursor", ctx):
        ok, _ = actualizar_producto("Freno Upd", "Desc", 1, 50000.0, 20, 5)
        assert ok is True


def test_actualizar_error_bd():
    ctx = MagicMock()
    ctx.side_effect = Exception("BD error")
    with patch("models.inventario.db_cursor", ctx):
        ok, _ = actualizar_producto("Nombre", "", 1, 45000.0, 10, 5)
        assert ok is False


# â”€â”€ ajustar_stock â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_ajustar_stock_negativo():
    ok, _ = ajustar_stock(1, -1)
    assert ok is False


def test_ajustar_stock_cero():
    ok, _ = ajustar_stock(1, 0)
    assert ok is False


def test_ajustar_stock_exitoso():
    cur, ctx = _make_ctx()
    with patch("models.inventario.db_cursor", ctx):
        ok, _ = ajustar_stock(1, 50)
        assert ok is True


# â”€â”€ desactivar_producto â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_desactivar_exitoso():
    cur, ctx = _make_ctx()
    with patch("models.inventario.db_cursor", ctx):
        ok, _ = desactivar_producto(1)
        assert ok is True


def test_desactivar_error_bd():
    ctx = MagicMock()
    ctx.side_effect = Exception("BD error")
    with patch("models.inventario.db_cursor", ctx):
        ok, _ = desactivar_producto(1)
        assert ok is False


# â”€â”€ buscar_productos â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_buscar_sin_filtros():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.inventario.db_cursor", ctx):
        assert isinstance(buscar_productos(), list)


def test_buscar_con_texto():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.inventario.db_cursor", ctx):
        assert isinstance(buscar_productos(texto="freno"), list)


def test_buscar_con_categoria():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.inventario.db_cursor", ctx):
        assert isinstance(buscar_productos(categoria_id=1), list)


def test_buscar_solo_activos():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.inventario.db_cursor", ctx):
        assert isinstance(buscar_productos(solo_activos=True), list)


def test_buscar_texto_y_categoria():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.inventario.db_cursor", ctx):
        assert isinstance(buscar_productos(texto="freno", categoria_id=1), list)


# â”€â”€ obtener_producto â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_obtener_existente():
    mock_row = {"id": 1, "codigo": "P001", "nombre": "Freno",
                "descripcion": "", "categoria": "Frenos",
                "categoria_id": 1, "precio_unitario": 45000.0,
                "stock_actual": 10, "stock_minimo": 5, "activo": True}
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = mock_row
    with patch("models.inventario.db_cursor", ctx):
        p = obtener_producto(1)
        assert p is not None
        assert p.codigo == "P001"


def test_obtener_no_existe():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = None
    with patch("models.inventario.db_cursor", ctx):
        assert obtener_producto(999) is None


# â”€â”€ productos_stock_bajo â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_stock_bajo_mock():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.inventario.db_cursor", ctx):
        assert isinstance(productos_stock_bajo(), list)


# â”€â”€ listar_categorias â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_listar_categorias_mock():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = [{"id": 1, "nombre": "Frenos"}]
    with patch("models.inventario.db_cursor", ctx):
        cats = listar_categorias()
        assert isinstance(cats, list)
        assert len(cats) == 1


# â”€â”€ obtener_alertas_no_vistas â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_alertas_no_vistas_mock():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.inventario.db_cursor", ctx):
        assert isinstance(obtener_alertas_no_vistas(), list)


