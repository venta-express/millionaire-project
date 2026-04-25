"""Tests unitarios para models/compras.py"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
from models.compras import Proveedor, Pedido


def test_proveedor_creacion():
    p = Proveedor(1, "RepCo", "Juan", "3001234567", "j@r.com", "900-1", True)
    assert p.id == 1
    assert p.nombre == "RepCo"
    assert p.activo is True

def test_proveedor_inactivo():
    p = Proveedor(2, "OldCo", "", "", "", "800-1", False)
    assert p.activo is False

def test_pedido_creacion():
    p = Pedido(1, "PED-001", 1, "RepCo", 1, "Admin",
               datetime.now(), date.today(), "Pendiente", "")
    assert p.numero_pedido == "PED-001"
    assert p.estado == "Pendiente"

def test_pedido_estados():
    for estado in ["Pendiente", "Recibido", "Cancelado"]:
        p = Pedido(1, "P", 1, "R", 1, "A", datetime.now(), date.today(), estado, "")
        assert p.estado == estado

def test_listar_proveedores_mock():
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.compras import listar_proveedores
        assert isinstance(listar_proveedores(), list)

def test_registrar_proveedor_campos_vacios():
    from models.compras import registrar_proveedor
    ok, msg = registrar_proveedor("", "", "", "", "")
    assert ok is False

def test_listar_pedidos_mock():
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.compras import listar_pedidos
        assert isinstance(listar_pedidos(), list)

def test_listar_proveedores_todos_mock():
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.compras import listar_proveedores
        assert isinstance(listar_proveedores(solo_activos=False), list)
