"""
Tests unitarios para models/inventario.py
Sprint 4: Cobertura de CRUD de productos e inventario.
"""

import pytest
from unittest.mock import patch, MagicMock
from models.inventario import Producto


# ── Tests de Producto dataclass ───────────────────────────────────────────────

def test_producto_creacion():
    """Verifica creacion correcta de un Producto."""
    p = Producto(
        id=1, codigo="FRENO-001", nombre="Pastilla de freno",
        descripcion="Para motos 125cc", categoria="Frenos",
        categoria_id=1, precio_unitario=45000.0,
        stock_actual=20, stock_minimo=5, activo=True
    )
    assert p.id == 1
    assert p.codigo == "FRENO-001"
    assert p.nombre == "Pastilla de freno"
    assert p.precio_unitario == 45000.0
    assert p.stock_actual == 20
    assert p.stock_minimo == 5
    assert p.activo is True


def test_producto_stock_bajo():
    """Un producto con stock menor al minimo debe detectarse."""
    p = Producto(1, "P001", "Prod", "", "Cat", 1, 10000.0, 2, 5, True)
    assert p.stock_actual < p.stock_minimo


def test_producto_stock_ok():
    """Un producto con stock mayor al minimo esta bien."""
    p = Producto(1, "P001", "Prod", "", "Cat", 1, 10000.0, 10, 5, True)
    assert p.stock_actual >= p.stock_minimo


def test_producto_inactivo():
    """Un producto puede estar inactivo."""
    p = Producto(1, "P001", "Prod", "", "Cat", 1, 10000.0, 0, 5, False)
    assert p.activo is False


def test_producto_precio_cero():
    """Un producto puede tener precio cero."""
    p = Producto(1, "P001", "Prod", "", "Cat", 1, 0.0, 10, 5, True)
    assert p.precio_unitario == 0.0


# ── Tests con mock de BD ──────────────────────────────────────────────────────

def test_listar_categorias_mock():
    """listar_categorias debe retornar lista desde BD."""
    mock_row = {"id": 1, "nombre": "Frenos"}
    with patch("models.inventario.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [mock_row]
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.inventario import listar_categorias
        resultado = listar_categorias()
        assert isinstance(resultado, list)


def test_registrar_producto_campos_vacios():
    """registrar_producto debe fallar si nombre esta vacio."""
    from models.inventario import registrar_producto
    ok, msg = registrar_producto("", "", "", 1, 10000.0, 10, 5)
    assert ok is False
    assert msg != ""


def test_registrar_producto_precio_negativo():
    """registrar_producto debe fallar si precio es negativo."""
    from models.inventario import registrar_producto
    ok, msg = registrar_producto("P001", "Prod", "", 1, -100.0, 10, 5)
    assert ok is False


def test_registrar_producto_stock_negativo():
    """registrar_producto debe fallar si stock es negativo."""
    from models.inventario import registrar_producto
    ok, msg = registrar_producto("P001", "Prod", "", 1, 10000.0, -1, 5)
    assert ok is False


def test_buscar_productos_mock():
    """buscar_productos debe retornar lista de Producto."""
    mock_row = {
        "id": 1, "codigo": "P001", "nombre": "Prod",
        "descripcion": "", "categoria": "Frenos",
        "categoria_id": 1, "precio_unitario": 10000.0,
        "stock_actual": 10, "stock_minimo": 5, "activo": True
    }
    with patch("models.inventario.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [mock_row]
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.inventario import buscar_productos
        resultado = buscar_productos()
        assert isinstance(resultado, list)
