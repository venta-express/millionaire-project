"""
Tests unitarios para models/compras.py
Sprint 4: Cobertura de proveedores y pedidos.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
from models.compras import Proveedor, Pedido


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


# ── Tests validaciones registrar_proveedor ────────────────────────────────────

def test_registrar_proveedor_nombre_vacio():
    from models.compras import registrar_proveedor
    ok, msg = registrar_proveedor("", "", "", "", "")
    assert ok is False
    assert "obligatorio" in msg.lower()


def test_registrar_proveedor_solo_espacios():
    from models.compras import registrar_proveedor
    ok, msg = registrar_proveedor("   ", "", "", "", "")
    assert ok is False


def test_registrar_proveedor_exitoso():
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.compras import registrar_proveedor
        ok, msg = registrar_proveedor("Repuestos SA", "Juan", "300", "rep@sa.com", "900")
        assert ok is True


def test_registrar_proveedor_nit_duplicado():
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_ctx.side_effect = Exception("unique constraint")
        from models.compras import registrar_proveedor
        ok, msg = registrar_proveedor("Repuestos SA", "Juan", "300", "rep@sa.com", "900")
        assert ok is False


# ── Tests listar_proveedores ──────────────────────────────────────────────────

def test_listar_proveedores_activos():
    mock_row = {"id": 1, "nombre": "Prov SA", "contacto": "Juan",
                "telefono": "300", "email": "p@p.com", "nit": "900", "activo": True}
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [mock_row]
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.compras import listar_proveedores
        resultado = listar_proveedores(solo_activos=True)
        assert isinstance(resultado, list)


def test_listar_proveedores_todos():
    mock_row = {"id": 1, "nombre": "Prov SA", "contacto": "Juan",
                "telefono": "300", "email": "p@p.com", "nit": "900", "activo": False}
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [mock_row]
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.compras import listar_proveedores
        resultado = listar_proveedores(solo_activos=False)
        assert isinstance(resultado, list)


# ── Tests registrar_pedido ────────────────────────────────────────────────────

def test_registrar_pedido_fecha_pasada():
    from models.compras import registrar_pedido
    fecha_pasada = date(2020, 1, 1)
    ok, msg = registrar_pedido(1, 1, fecha_pasada, "")
    assert ok is False


def test_registrar_pedido_exitoso():
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = {"id": 1}
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.compras import registrar_pedido
        fecha_futura = date(2030, 12, 31)
        ok, msg, _ = registrar_pedido(1, 1, fecha_futura, "Nota")
        assert ok is True


# ── Tests listar_pedidos ──────────────────────────────────────────────────────

def test_listar_pedidos_sin_filtro():
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.compras import listar_pedidos
        resultado = listar_pedidos()
        assert isinstance(resultado, list)


def test_listar_pedidos_con_estado():
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.compras import listar_pedidos
        resultado = listar_pedidos(estado="Pendiente")
        assert isinstance(resultado, list)


# ── Tests actualizar_estado_pedido ────────────────────────────────────────────

def test_actualizar_estado_pedido_invalido():
    from models.compras import actualizar_estado_pedido
    ok, msg = actualizar_estado_pedido(1, "EstadoInexistente")
    assert ok is False


def test_actualizar_estado_pedido_valido():
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.compras import actualizar_estado_pedido
        ok, msg = actualizar_estado_pedido(1, "Recibido")
        assert ok is True


# ── Tests pedidos_pendientes_vencidos ─────────────────────────────────────────

def test_pedidos_pendientes_vencidos_mock():
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.compras import pedidos_pendientes_vencidos
        resultado = pedidos_pendientes_vencidos()
        assert isinstance(resultado, list)


# ── Tests actualizar_proveedor ────────────────────────────────────────────────

def test_actualizar_proveedor_nombre_vacio():
    from models.compras import actualizar_proveedor
    ok, msg = actualizar_proveedor(1, "", "", "", "", "")
    assert ok is False


def test_actualizar_proveedor_exitoso():
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.compras import actualizar_proveedor
        ok, msg = actualizar_proveedor(1, "Nuevo Nombre", "Cont", "Tel", "Email", "NIT")
        assert ok is True


# ── Tests desactivar_proveedor ────────────────────────────────────────────────

def test_desactivar_proveedor_mock():
    with patch("models.compras.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.compras import desactivar_proveedor
        ok, msg = desactivar_proveedor(1)
        assert ok is True
