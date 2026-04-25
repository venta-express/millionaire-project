"""
Tests unitarios para models/backup.py
Sprint 4: Cobertura de backup y listado de archivos.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from models.backup import listar_backups


def test_listar_backups_directorio_inexistente():
    """listar_backups debe retornar lista vacia si no existe el directorio."""
    resultado = listar_backups("/ruta/que/no/existe")
    assert resultado == []


def test_listar_backups_directorio_vacio():
    """listar_backups debe retornar lista vacia en directorio vacio."""
    with tempfile.TemporaryDirectory() as tmpdir:
        resultado = listar_backups(tmpdir)
        assert resultado == []


def test_listar_backups_con_archivos():
    """listar_backups debe encontrar archivos de backup."""
    with tempfile.TemporaryDirectory() as tmpdir:
        nombre = "autoparts_backup_20260424_120000.sql"
        ruta = os.path.join(tmpdir, nombre)
        with open(ruta, "w") as f:
            f.write("-- backup sql")
        resultado = listar_backups(tmpdir)
        assert len(resultado) == 1
        assert resultado[0]["nombre"] == nombre


def test_listar_backups_ignora_otros_archivos():
    """listar_backups debe ignorar archivos que no sean backups."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "otro.txt"), "w") as f:
            f.write("no es backup")
        resultado = listar_backups(tmpdir)
        assert resultado == []


def test_listar_backups_ordenados_por_fecha():
    """listar_backups debe retornar backups ordenados por fecha desc."""
    with tempfile.TemporaryDirectory() as tmpdir:
        for ts in ["20260101_100000", "20260424_120000"]:
            nombre = f"autoparts_backup_{ts}.sql"
            with open(os.path.join(tmpdir, nombre), "w") as f:
                f.write("-- backup")
        resultado = listar_backups(tmpdir)
        assert len(resultado) == 2
        assert resultado[0]["fecha"] >= resultado[1]["fecha"]


def test_listar_backups_contiene_campos():
    """listar_backups debe retornar dicts con campos esperados."""
    with tempfile.TemporaryDirectory() as tmpdir:
        nombre = "autoparts_backup_20260424_120000.sql"
        with open(os.path.join(tmpdir, nombre), "w") as f:
            f.write("-- backup test")
        resultado = listar_backups(tmpdir)
        assert "nombre" in resultado[0]
        assert "ruta" in resultado[0]
        assert "tamano_kb" in resultado[0]
        assert "fecha" in resultado[0]


def test_generar_backup_sin_pgdump():
    """generar_backup debe retornar False si pg_dump no existe."""
    with patch("models.backup.DB_CONFIG", {
        "host": "localhost", "port": 5432,
        "dbname": "test", "user": "postgres", "password": ""
    }):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("pg_dump no encontrado")
            from models.backup import generar_backup
            with tempfile.TemporaryDirectory() as tmpdir:
                ok, msg = generar_backup(tmpdir)
                assert ok is False
                assert "pg_dump" in msg
