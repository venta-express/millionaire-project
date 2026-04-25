"""
Tests unitarios para models/configuracion.py
Sprint 4: Cobertura de configuracion del sistema.
"""

import pytest
from unittest.mock import patch, MagicMock
from models.configuracion import (
    obtener_config, obtener_todas, actualizar_config, obtener_info_empresa,
)


def _make_ctx(cur=None):
    if cur is None:
        cur = MagicMock()
    ctx = MagicMock()
    ctx.return_value.__enter__ = MagicMock(return_value=cur)
    ctx.return_value.__exit__ = MagicMock(return_value=False)
    return cur, ctx


# ── obtener_config ────────────────────────────────────────────────────────────

def test_obtener_config_default():
    """obtener_config debe retornar default si BD falla."""
    ctx = MagicMock()
    ctx.side_effect = Exception("BD no disponible")
    with patch("models.configuracion.db_cursor", ctx):
        resultado = obtener_config("clave_inexistente", "valor_default")
        assert resultado == "valor_default"


def test_obtener_config_existente():
    """obtener_config debe retornar el valor de la BD."""
    mock_row = {"valor": "AutoParts Express"}
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = mock_row
    with patch("models.configuracion.db_cursor", ctx):
        resultado = obtener_config("empresa_nombre")
        assert resultado == "AutoParts Express"


def test_obtener_config_none_retorna_default():
    """obtener_config debe retornar default si no hay fila."""
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = None
    with patch("models.configuracion.db_cursor", ctx):
        resultado = obtener_config("no_existe", "default")
        assert resultado == "default"


# ── obtener_todas ─────────────────────────────────────────────────────────────

def test_obtener_todas_mock():
    """obtener_todas debe retornar lista de configuraciones."""
    mock_rows = [
        {"id": 1, "clave": "empresa_nombre", "valor": "AutoParts",
         "descripcion": "Nombre", "actualizado_en": None},
    ]
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = mock_rows
    with patch("models.configuracion.db_cursor", ctx):
        resultado = obtener_todas()
        assert isinstance(resultado, list)
        assert len(resultado) == 1


def test_obtener_todas_vacia():
    """obtener_todas con tabla vacia retorna lista vacia."""
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.configuracion.db_cursor", ctx):
        resultado = obtener_todas()
        assert resultado == []


# ── actualizar_config ─────────────────────────────────────────────────────────

def test_actualizar_config_exitoso():
    """actualizar_config debe retornar True si la BD funciona."""
    cur, ctx = _make_ctx()
    with patch("models.configuracion.db_cursor", ctx):
        resultado = actualizar_config("empresa_nombre", "Nuevo Nombre")
        assert resultado is True


def test_actualizar_config_falla():
    """actualizar_config debe retornar False si la BD falla."""
    ctx = MagicMock()
    ctx.side_effect = Exception("Error BD")
    with patch("models.configuracion.db_cursor", ctx):
        resultado = actualizar_config("clave", "valor")
        assert resultado is False


# ── obtener_info_empresa ──────────────────────────────────────────────────────

def test_obtener_info_empresa_mock():
    """obtener_info_empresa debe retornar dict con datos de empresa."""
    mock_rows = [
        {"clave": "empresa_nombre", "valor": "AutoParts Express"},
        {"clave": "empresa_nit", "valor": "900000000-0"},
    ]
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = mock_rows
    with patch("models.configuracion.db_cursor", ctx):
        resultado = obtener_info_empresa()
        assert isinstance(resultado, dict)
        assert "empresa_nombre" in resultado


def test_obtener_info_empresa_vacia():
    """obtener_info_empresa con BD vacia retorna dict vacío o con defaults."""
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.configuracion.db_cursor", ctx):
        resultado = obtener_info_empresa()
        assert isinstance(resultado, dict)
