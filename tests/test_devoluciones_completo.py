"""Tests completos para models/devoluciones.py"""
import pytest
from unittest.mock import patch, MagicMock


def test_actualizar_estado_devolucion_invalido():
    from models.devoluciones import actualizar_estado_devolucion
    ok, _ = actualizar_estado_devolucion(1, "EstadoInvalido")
    assert ok is False


def test_actualizar_estado_devolucion_valido():
    from models.devoluciones import actualizar_estado_devolucion
    row = {"producto_id": 1, "cantidad": 5, "estado": "Pendiente"}
    with patch("models.devoluciones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = row
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _ = actualizar_estado_devolucion(1, "Procesada")
        assert ok is True


def test_actualizar_estado_devolucion_no_existe():
    from models.devoluciones import actualizar_estado_devolucion
    with patch("models.devoluciones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = None
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        ok, _ = actualizar_estado_devolucion(999, "Procesada")
        assert ok is False


def test_listar_devoluciones_con_estado():
    from models.devoluciones import listar_devoluciones
    with patch("models.devoluciones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        resultado = listar_devoluciones(estado="Pendiente")
        assert isinstance(resultado, list)


def test_listar_devoluciones_con_proveedor():
    from models.devoluciones import listar_devoluciones
    with patch("models.devoluciones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        resultado = listar_devoluciones(proveedor_id=1)
        assert isinstance(resultado, list)

