"""
Tests unitarios para models/devoluciones.py
Sprint 4: Cobertura de devoluciones a proveedores.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from models.devoluciones import (
    Devolucion,
    registrar_devolucion, listar_devoluciones, actualizar_estado_devolucion,
)


def _make_ctx(cur=None):
    if cur is None:
        cur = MagicMock()
    ctx = MagicMock()
    ctx.return_value.__enter__ = MagicMock(return_value=cur)
    ctx.return_value.__exit__ = MagicMock(return_value=False)
    return cur, ctx


# â”€â”€ Tests dataclass â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_devolucion_creacion():
    d = Devolucion(
        id=1, numero_dev="DEV-20260424-0001",
        proveedor_id=1, proveedor_nombre="Repuestos SA",
        producto_id=1, producto_nombre="Freno", producto_codigo="FRN-001",
        usuario_id=1, usuario_nombre="Admin",
        cantidad=2, motivo="Producto defectuoso",
        estado="Pendiente", fecha=datetime.now()
    )
    assert d.numero_dev == "DEV-20260424-0001"
    assert d.estado == "Pendiente"
    assert d.cantidad == 2


def test_devolucion_estados():
    for estado in ("Pendiente", "Procesada", "Rechazada"):
        d = Devolucion(1, "DEV-001", 1, "Prov", 1, "Prod", "P001",
                       1, "Admin", 1, "motivo", estado, datetime.now())
        assert d.estado == estado


# â”€â”€ Tests registrar_devolucion â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_registrar_devolucion_cantidad_cero():
    ok, _, _ = registrar_devolucion(1, 1, 1, 0, "motivo")
    assert ok is False
    assert "cantidad" in msg.lower()


def test_registrar_devolucion_cantidad_negativa():
    ok, _, _ = registrar_devolucion(1, 1, 1, -5, "motivo")
    assert ok is False


def test_registrar_devolucion_motivo_vacio():
    ok, _, _ = registrar_devolucion(1, 1, 1, 3, "")
    assert ok is False
    assert "motivo" in msg.lower()


def test_registrar_devolucion_motivo_espacios():
    ok, _, _ = registrar_devolucion(1, 1, 1, 3, "   ")
    assert ok is False


def test_registrar_devolucion_exitosa():
    """
    Simula el flujo exitoso. Se configuran dos llamadas a fetchone:
    la primera para el contador interno del numero de devolucion,
    la segunda para el RETURNING id del INSERT.
    """
    _, ctx = _make_ctx()
    cur.fetchone.side_effect = [
        {"total": 5},   # _generar_numero_dev: conteo existente
        {"id": 1},      # INSERT RETURNING id
    ]
    with patch("models.devoluciones.db_cursor", ctx):
        ok, numero, _ = registrar_devolucion(1, 1, 1, 2, "Defectuoso")
        assert ok is True
        assert numero.startswith("DEV-")


def test_registrar_devolucion_error_bd():
    """Si la BD falla, registrar_devolucion debe retornar ok=False."""
    ctx = MagicMock()
    ctx.side_effect = Exception("BD caida")
    with patch("models.devoluciones.db_cursor", ctx):
        ok, _, _ = registrar_devolucion(1, 1, 1, 2, "Defectuoso")
        assert ok is False


# â”€â”€ Tests listar_devoluciones â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_listar_devoluciones_sin_filtros():
    _, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.devoluciones.db_cursor", ctx):
        resultado = listar_devoluciones()
        assert isinstance(resultado, list)


def test_listar_devoluciones_por_estado():
    _, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.devoluciones.db_cursor", ctx):
        resultado = listar_devoluciones(estado="Pendiente")
        assert isinstance(resultado, list)


def test_listar_devoluciones_por_proveedor():
    _, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.devoluciones.db_cursor", ctx):
        resultado = listar_devoluciones(proveedor_id=1)
        assert isinstance(resultado, list)


def test_listar_devoluciones_ambos_filtros():
    _, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.devoluciones.db_cursor", ctx):
        resultado = listar_devoluciones(estado="Procesada", proveedor_id=2)
        assert isinstance(resultado, list)


# â”€â”€ Tests actualizar_estado_devolucion â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_actualizar_estado_devolucion_invalido():
    ok, _ = actualizar_estado_devolucion(1, "EstadoMalo")
    assert ok is False


def test_actualizar_estado_devolucion_procesada():
    _, ctx = _make_ctx()
    with patch("models.devoluciones.db_cursor", ctx):
        ok, _ = actualizar_estado_devolucion(1, "Procesada")
        assert ok is True


def test_actualizar_estado_devolucion_rechazada():
    _, ctx = _make_ctx()
    with patch("models.devoluciones.db_cursor", ctx):
        ok, _ = actualizar_estado_devolucion(1, "Rechazada")
        assert ok is True


def test_actualizar_estado_devolucion_error_bd():
    ctx = MagicMock()
    ctx.side_effect = Exception("BD caida")
    with patch("models.devoluciones.db_cursor", ctx):
        ok, _ = actualizar_estado_devolucion(1, "Procesada")
        assert ok is False


