"""Tests completos para models/inventario.py"""
import pytest
from unittest.mock import patch, MagicMock
from models.inventario import Producto


def test_ajustar_stock_negativo():
    from models.inventario import ajustar_stock
    ok, _ = ajustar_stock(1, -5)
    assert ok is False


def test_ajustar_stock_cero():
    from models.inventario import ajustar_stock
    with patch("models.inventario.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        with patch("models.inventario._registrar_alerta_si_necesario"):
            ok, _ = ajustar_stock(1, 0)
            assert ok is True


def test_desactivar_producto_mock():
    from models.inventario import desactivar_producto
    with patch("models.inventario.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _ = desactivar_producto(1)
        assert ok is True


def test_buscar_productos_con_texto():
    from models.inventario import buscar_productos
    with patch("models.inventario.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        resultado = buscar_productos(texto="freno")
        assert isinstance(resultado, list)


def test_buscar_productos_con_categoria():
    from models.inventario import buscar_productos
    with patch("models.inventario.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        resultado = buscar_productos(categoria_id=1)
        assert isinstance(resultado, list)


def test_buscar_productos_todos():
    from models.inventario import buscar_productos
    with patch("models.inventario.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        resultado = buscar_productos(solo_activos=False)
        assert isinstance(resultado, list)


def test_obtener_producto_mock():
    from models.inventario import obtener_producto
    mock_row = {
        "id": 1, "codigo": "P001", "nombre": "Prod",
        "descripcion": "", "categoria": "Frenos",
        "categoria_id": 1, "precio_unitario": 10000.0,
        "stock_actual": 10, "stock_minimo": 5, "activo": True
    }
    with patch("models.inventario.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = mock_row
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        p = obtener_producto(1)
        assert p is not None
        assert p.id == 1


def test_obtener_producto_no_existe():
    from models.inventario import obtener_producto
    with patch("models.inventario.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = None
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        p = obtener_producto(999)
        assert p is None


def test_productos_stock_bajo_mock():
    from models.inventario import productos_stock_bajo
    with patch("models.inventario.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        resultado = productos_stock_bajo()
        assert isinstance(resultado, list)


def test_obtener_alertas_no_vistas_mock():
    from models.inventario import obtener_alertas_no_vistas
    with patch("models.inventario.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        resultado = obtener_alertas_no_vistas()
        assert isinstance(resultado, list)


def test_marcar_alertas_vistas_mock():
    from models.inventario import marcar_alertas_vistas
    with patch("models.inventario.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        marcar_alertas_vistas()
        assert mock_cur.execute.called


def test_actualizar_producto_mock():
    from models.inventario import actualizar_producto
    with patch("models.inventario.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _ = actualizar_producto(1, "Prod", "", 1, 10000.0, 5)
        assert ok is True

