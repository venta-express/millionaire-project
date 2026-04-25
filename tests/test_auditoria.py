"""
Tests unitarios para models/auditoria.py
Sprint 4: Cobertura de registro y consulta de auditoria.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


def test_registrar_accion_mock():
    """registrar_accion debe insertar en la BD sin errores."""
    with patch("models.auditoria.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.auditoria import registrar_accion
        registrar_accion(1, "CREAR_VENTA", "Ventas", {"total": 50000})
        assert mock_cur.execute.called


def test_registrar_accion_sin_detalle():
    """registrar_accion debe funcionar sin detalle."""
    with patch("models.auditoria.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.auditoria import registrar_accion
        registrar_accion(1, "LOGIN", "Sistema")
        assert mock_cur.execute.called


def test_obtener_auditoria_sin_filtros():
    """obtener_auditoria debe retornar lista de registros."""
    mock_rows = [
        {
            "id": 1, "usuario": "admin", "username": "admin",
            "accion": "LOGIN", "modulo": "Sistema",
            "detalle": None, "fecha_hora": datetime.now(), "ip": "127.0.0.1"
        }
    ]
    with patch("models.auditoria.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = mock_rows
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.auditoria import obtener_auditoria
        resultado = obtener_auditoria()
        assert isinstance(resultado, list)


def test_obtener_auditoria_con_modulo():
    """obtener_auditoria debe filtrar por modulo."""
    with patch("models.auditoria.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.auditoria import obtener_auditoria
        resultado = obtener_auditoria(modulo="Ventas")
        assert isinstance(resultado, list)


def test_obtener_auditoria_con_usuario():
    """obtener_auditoria debe filtrar por usuario_id."""
    with patch("models.auditoria.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.auditoria import obtener_auditoria
        resultado = obtener_auditoria(usuario_id=1)
        assert isinstance(resultado, list)


def test_obtener_auditoria_con_ambos_filtros():
    """obtener_auditoria debe filtrar por modulo y usuario."""
    with patch("models.auditoria.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.auditoria import obtener_auditoria
        resultado = obtener_auditoria(modulo="Ventas", usuario_id=1)
        assert isinstance(resultado, list)
