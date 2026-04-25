"""
Tests unitarios para models/configuracion.py
Sprint 4: Cobertura de configuracion del sistema.
"""

import pytest
from unittest.mock import patch, MagicMock


def test_obtener_config_default():
    """obtener_config debe retornar default si BD falla."""
    with patch("models.configuracion.db_cursor") as mock_ctx:
        mock_ctx.side_effect = Exception("BD no disponible")
        from models.configuracion import obtener_config
        resultado = obtener_config("clave_inexistente", "valor_default")
        assert resultado == "valor_default"


def test_obtener_config_existente():
    """obtener_config debe retornar el valor de la BD."""
    mock_row = {"valor": "AutoParts Express"}
    with patch("models.configuracion.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = mock_row
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.configuracion import obtener_config
        resultado = obtener_config("empresa_nombre")
        assert resultado == "AutoParts Express"


def test_obtener_config_none_retorna_default():
    """obtener_config debe retornar default si no hay fila."""
    with patch("models.configuracion.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = None
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.configuracion import obtener_config
        resultado = obtener_config("no_existe", "default")
        assert resultado == "default"


def test_obtener_todas_mock():
    """obtener_todas debe retornar lista de configuraciones."""
    mock_rows = [
        {"id": 1, "clave": "empresa_nombre", "valor": "AutoParts",
         "descripcion": "Nombre", "actualizado_en": None},
    ]
    with patch("models.configuracion.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = mock_rows
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.configuracion import obtener_todas
        resultado = obtener_todas()
        assert isinstance(resultado, list)
        assert len(resultado) == 1


def test_actualizar_config_exitoso():
    """actualizar_config debe retornar True si la BD funciona."""
    with patch("models.configuracion.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.configuracion import actualizar_config
        resultado = actualizar_config("empresa_nombre", "Nuevo Nombre")
        assert resultado is True


def test_actualizar_config_falla():
    """actualizar_config debe retornar False si la BD falla."""
    with patch("models.configuracion.db_cursor") as mock_ctx:
        mock_ctx.side_effect = Exception("Error BD")
        from models.configuracion import actualizar_config
        resultado = actualizar_config("clave", "valor")
        assert resultado is False


def test_obtener_info_empresa_mock():
    """obtener_info_empresa debe retornar dict con datos de empresa."""
    mock_rows = [
        {"clave": "empresa_nombre", "valor": "AutoParts Express"},
        {"clave": "empresa_nit", "valor": "900000000-0"},
    ]
    with patch("models.configuracion.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = mock_rows
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.configuracion import obtener_info_empresa
        resultado = obtener_info_empresa()
        assert isinstance(resultado, dict)
        assert "empresa_nombre" in resultado
