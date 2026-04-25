"""Tests unitarios para models/devoluciones.py"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from models.devoluciones import Devolucion


def test_devolucion_creacion():
    d = Devolucion(
        id=1, numero_dev="DEV-20260424-0001",
        proveedor_id=1, proveedor_nombre="RepCo",
        producto_id=1, producto_nombre="Freno",
        producto_codigo="FRN-001", usuario_id=1,
        usuario_nombre="Admin", cantidad=5,
        motivo="Defectuoso", estado="Pendiente",
        fecha=datetime.now()
    )
    assert d.numero_dev == "DEV-20260424-0001"
    assert d.estado == "Pendiente"
    assert d.cantidad == 5

def test_devolucion_estados():
    for estado in ["Pendiente", "Procesada", "Rechazada"]:
        d = Devolucion(1, "D", 1, "R", 1, "P", "C", 1, "A", 1, "M", estado, datetime.now())
        assert d.estado == estado

def test_registrar_devolucion_cantidad_cero():
    from models.devoluciones import registrar_devolucion
    ok, msg, _ = registrar_devolucion(1, 1, 1, 0, "Motivo")
    assert ok is False

def test_registrar_devolucion_motivo_vacio():
    from models.devoluciones import registrar_devolucion
    ok, msg, _ = registrar_devolucion(1, 1, 1, 5, "")
    assert ok is False

def test_listar_devoluciones_mock():
    with patch("models.devoluciones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.devoluciones import listar_devoluciones
        assert isinstance(listar_devoluciones(), list)
