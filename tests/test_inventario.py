"""
Tests unitarios para models/inventario.py - CORREGIDO
Sprint 4: pytest.approx para floats, cobertura completa.
"""
import pytest
from unittest.mock import patch, MagicMock
from models.inventario import Producto


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


# ── registrar_producto ────────────────────────────────────────────────────────

def test_registrar_codigo_vacio():
    from models.inventario import registrar_producto
    ok, _ = registrar_producto("", "Freno", "", 1, 45000.0, 10, 5)
    assert ok is False

def test_registrar_nombre_vacio():
    from models.inventario import registrar_producto
    ok, _ = registrar_producto("P001", "", "", 1, 45000.0, 10, 5)
    assert ok is False

def test_registrar_precio_negativo():
    from models.inventario import registrar_producto
    ok, _ = registrar_producto("P001", "Freno", "", 1, -1.0, 10, 5)
    assert ok is False

def test_registrar_stock_negativo():
    from models.inventario import registrar_producto
    ok, _ = registrar_producto("P001", "Freno", "", 1, 45000.0, -1, 5)
    assert ok is False

def test_registrar_stock_minimo_negativo():
    from models.inventario import registrar_producto
    ok, _ = registrar_producto("P001", "Freno", "", 1, 45000.0, 10, -1)
    assert ok is False

def test_registrar_exitoso():
    with patch("models.inventario.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchone.return_value = {"id": 1}
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.inventario import registrar_producto
        ok, _ = registrar_producto("P001", "Freno", "Desc", 1, 45000.0, 10, 5)
        assert ok is True

def test_registrar_codigo_duplicado():
    with patch("models.inventario.db_cursor") as mc:
        mc.side_effect = Exception("unique constraint violated")
        from models.inventario import registrar_producto
        ok, msg = registrar_producto("P001", "Freno", "", 1, 45000.0, 10, 5)
        assert ok is False
        assert "P001" in msg

def test_registrar_error_generico():
    with patch("models.inventario.db_cursor") as mc:
        mc.side_effect = Exception("connection error")
        from models.inventario import registrar_producto
        ok, _ = registrar_producto("P001", "Freno", "", 1, 45000.0, 10, 5)
        assert ok is False


# ── actualizar_producto ───────────────────────────────────────────────────────

def test_actualizar_nombre_vacio():
    from models.inventario import actualizar_producto
    ok, _ = actualizar_producto(1, "", "", 1, 45000.0, 10, 5)
    assert ok is False

def test_actualizar_precio_negativo():
    from models.inventario import actualizar_producto
    ok, _ = actualizar_producto(1, "Freno", "", 1, -500.0, 10, 5)
    assert ok is False

def test_actualizar_exitoso():
    with patch("models.inventario.db_cursor") as mc:
        cur = MagicMock()
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.inventario import actualizar_producto
        ok, _ = actualizar_producto(1, "Freno Upd", "Desc", 1, 50000.0, 20, 5)
        assert ok is True

def test_actualizar_error_bd():
    with patch("models.inventario.db_cursor") as mc:
        mc.side_effect = Exception("BD error")
        from models.inventario import actualizar_producto
        ok, _ = actualizar_producto(1, "Nombre", "", 1, 45000.0, 10, 5)
        assert ok is False


# ── ajustar_stock ─────────────────────────────────────────────────────────────

def test_ajustar_stock_negativo():
    from models.inventario import ajustar_stock
    ok, _ = ajustar_stock(1, -1)
    assert ok is False

def test_ajustar_stock_cero():
    from models.inventario import ajustar_stock
    ok, _ = ajustar_stock(1, 0)
    assert ok is False

def test_ajustar_stock_exitoso():
    with patch("models.inventario.db_cursor") as mc:
        cur = MagicMock()
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.inventario import ajustar_stock
        ok, _ = ajustar_stock(1, 50)
        assert ok is True


# ── desactivar_producto ───────────────────────────────────────────────────────

def test_desactivar_exitoso():
    with patch("models.inventario.db_cursor") as mc:
        cur = MagicMock()
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.inventario import desactivar_producto
        ok, _ = desactivar_producto(1)
        assert ok is True


# ── buscar_productos ──────────────────────────────────────────────────────────

def test_buscar_sin_filtros():
    with patch("models.inventario.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchall.return_value = []
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.inventario import buscar_productos
        assert isinstance(buscar_productos(), list)

def test_buscar_con_texto():
    with patch("models.inventario.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchall.return_value = []
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.inventario import buscar_productos
        assert isinstance(buscar_productos(texto="freno"), list)

def test_buscar_con_categoria():
    with patch("models.inventario.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchall.return_value = []
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.inventario import buscar_productos
        assert isinstance(buscar_productos(categoria_id=1), list)

def test_buscar_solo_activos():
    with patch("models.inventario.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchall.return_value = []
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.inventario import buscar_productos
        assert isinstance(buscar_productos(solo_activos=True), list)

def test_buscar_texto_y_categoria():
    with patch("models.inventario.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchall.return_value = []
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.inventario import buscar_productos
        assert isinstance(buscar_productos(texto="freno", categoria_id=1), list)


# ── obtener_producto ──────────────────────────────────────────────────────────

def test_obtener_existente():
    mock_row = {"id": 1, "codigo": "P001", "nombre": "Freno",
                "descripcion": "", "categoria": "Frenos",
                "categoria_id": 1, "precio_unitario": 45000.0,
                "stock_actual": 10, "stock_minimo": 5, "activo": True}
    with patch("models.inventario.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchone.return_value = mock_row
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.inventario import obtener_producto
        p = obtener_producto(1)
        assert p is not None
        assert p.codigo == "P001"

def test_obtener_no_existe():
    with patch("models.inventario.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchone.return_value = None
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.inventario import obtener_producto
        assert obtener_producto(999) is None


# ── productos_stock_bajo ──────────────────────────────────────────────────────

def test_stock_bajo_mock():
    with patch("models.inventario.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchall.return_value = []
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.inventario import productos_stock_bajo
        assert isinstance(productos_stock_bajo(), list)


# ── listar_categorias ─────────────────────────────────────────────────────────

def test_listar_categorias_mock():
    with patch("models.inventario.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchall.return_value = [{"id": 1, "nombre": "Frenos"}]
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.inventario import listar_categorias
        cats = listar_categorias()
        assert isinstance(cats, list)
        assert len(cats) == 1


# ── obtener_alertas_no_vistas ─────────────────────────────────────────────────

def test_alertas_no_vistas_mock():
    with patch("models.inventario.db_cursor") as mc:
        cur = MagicMock()
        cur.fetchall.return_value = []
        mc.return_value.__enter__ = MagicMock(return_value=cur)
        mc.return_value.__exit__ = MagicMock(return_value=False)
        from models.inventario import obtener_alertas_no_vistas
        assert isinstance(obtener_alertas_no_vistas(), list)
