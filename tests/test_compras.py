"""
Tests unitarios para models/compras.py
Sprint 4: Cobertura de proveedores y pedidos.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
from models.compras import (
    Proveedor, Pedido,
    registrar_proveedor, listar_proveedores,
    registrar_pedido, listar_pedidos,
    actualizar_estado_pedido, pedidos_pendientes_vencidos,
    actualizar_proveedor, desactivar_proveedor,
)


def _make_ctx(cur=None):
    if cur is None:
        cur = MagicMock()
    ctx = MagicMock()
    ctx.return_value.__enter__ = MagicMock(return_value=cur)
    ctx.return_value.__exit__ = MagicMock(return_value=False)
    return cur, ctx


# ── Tests dataclasses ─────────────────────────────────────────────────────────

def test_proveedor_creacion():
    p = Proveedor(1, "Repuestos SA", "Juan", "3001234567", "rep@sa.com", "900123456-0", True)
    assert p.id == 1
    assert p.nombre == "Repuestos SA"
    assert p.nit == "900123456-0"
    assert p.activo is True


def test_proveedor_inactivo():
    p = Proveedor(2, "Moto Parts", "", "", "", "", False)
    assert p.activo is False


def test_proveedor_igualdad():
    p1 = Proveedor(1, "A", "B", "C", "D", "E", True)
    p2 = Proveedor(1, "A", "B", "C", "D", "E", True)
    assert p1 == p2


def test_pedido_creacion():
    p = Pedido(
        id=1, numero_pedido="PED-20260424-0001",
        proveedor_id=1, proveedor_nombre="Repuestos SA",
        usuario_id=1, usuario_nombre="Admin",
        fecha_pedido=datetime.now(), fecha_estimada=date.today(),
        estado="Pendiente", notas=""
    )
    assert p.numero_pedido == "PED-20260424-0001"
    assert p.estado == "Pendiente"


def test_pedido_estados():
    for estado in ("Pendiente", "Recibido", "Cancelado"):
        p = Pedido(1, "PED-001", 1, "Prov", 1, "Admin",
                   datetime.now(), date.today(), estado, "")
        assert p.estado == estado


# ── Tests registrar_proveedor ─────────────────────────────────────────────────

def test_registrar_proveedor_nombre_vacio():
    ok, msg = registrar_proveedor("", "", "", "", "")
    assert ok is False
    assert "obligatorio" in msg.lower()


def test_registrar_proveedor_solo_espacios():
    ok, msg = registrar_proveedor("   ", "", "", "", "")
    assert ok is False


def test_registrar_proveedor_exitoso():
    cur, ctx = _make_ctx()
    with patch("models.compras.db_cursor", ctx):
        ok, msg = registrar_proveedor("Repuestos SA", "Juan", "300", "rep@sa.com", "900")
        assert ok is True


def test_registrar_proveedor_nit_duplicado():
    ctx = MagicMock()
    ctx.side_effect = Exception("unique constraint")
    with patch("models.compras.db_cursor", ctx):
        ok, msg = registrar_proveedor("Repuestos SA", "Juan", "300", "rep@sa.com", "900")
        assert ok is False


# ── Tests listar_proveedores ──────────────────────────────────────────────────

def test_listar_proveedores_activos():
    mock_row = {"id": 1, "nombre": "Prov SA", "contacto": "Juan",
                "telefono": "300", "email": "p@p.com", "nit": "900", "activo": True}
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = [mock_row]
    with patch("models.compras.db_cursor", ctx):
        resultado = listar_proveedores(solo_activos=True)
        assert isinstance(resultado, list)


def test_listar_proveedores_todos():
    mock_row = {"id": 1, "nombre": "Prov SA", "contacto": "Juan",
                "telefono": "300", "email": "p@p.com", "nit": "900", "activo": False}
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = [mock_row]
    with patch("models.compras.db_cursor", ctx):
        resultado = listar_proveedores(solo_activos=False)
        assert isinstance(resultado, list)


# ── Tests registrar_pedido ────────────────────────────────────────────────────

def test_registrar_pedido_fecha_pasada():
    """fecha_estimada en el pasado debe fallar — retorna (ok, msg) o (ok, msg, id)."""
    fecha_pasada = date(2020, 1, 1)
    resultado = registrar_pedido(1, 1, fecha_pasada, "")
    # Aceptamos 2 o 3 valores de retorno segun la implementacion
    ok = resultado[0]
    assert ok is False


def test_registrar_pedido_exitoso():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = {"id": 1}
    with patch("models.compras.db_cursor", ctx):
        fecha_futura = date(2030, 12, 31)
        resultado = registrar_pedido(1, 1, fecha_futura, "Nota")
        ok = resultado[0]
        assert ok is True


# ── Tests listar_pedidos ──────────────────────────────────────────────────────

def test_listar_pedidos_sin_filtro():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.compras.db_cursor", ctx):
        resultado = listar_pedidos()
        assert isinstance(resultado, list)


def test_listar_pedidos_con_estado():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.compras.db_cursor", ctx):
        resultado = listar_pedidos(estado="Pendiente")
        assert isinstance(resultado, list)


# ── Tests actualizar_estado_pedido ────────────────────────────────────────────

def test_actualizar_estado_pedido_invalido():
    ok, msg = actualizar_estado_pedido(1, "EstadoInexistente")
    assert ok is False


def test_actualizar_estado_pedido_valido():
    cur, ctx = _make_ctx()
    with patch("models.compras.db_cursor", ctx):
        ok, msg = actualizar_estado_pedido(1, "Recibido")
        assert ok is True


# ── Tests pedidos_pendientes_vencidos ─────────────────────────────────────────

def test_pedidos_pendientes_vencidos_mock():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.compras.db_cursor", ctx):
        resultado = pedidos_pendientes_vencidos()
        assert isinstance(resultado, list)


# ── Tests actualizar_proveedor ────────────────────────────────────────────────

def test_actualizar_proveedor_nombre_vacio():
    ok, msg = actualizar_proveedor(1, "", "", "", "", "")
    assert ok is False


def test_actualizar_proveedor_exitoso():
    cur, ctx = _make_ctx()
    with patch("models.compras.db_cursor", ctx):
        ok, msg = actualizar_proveedor(1, "Nuevo Nombre", "Cont", "Tel", "Email", "NIT")
        assert ok is True


# ── Tests desactivar_proveedor ────────────────────────────────────────────────

def test_desactivar_proveedor_mock():
    cur, ctx = _make_ctx()
    with patch("models.compras.db_cursor", ctx):
        ok, msg = desactivar_proveedor(1)
        assert ok is True
