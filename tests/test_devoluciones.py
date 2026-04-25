"""
Tests unitarios para models/devoluciones.py
Sprint 4: Cobertura de devoluciones a proveedores.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from models.devoluciones import Devolucion


# ── Tests dataclass ───────────────────────────────────────────────────────────

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


# ── Tests validaciones registrar_devolucion ───────────────────────────────────

def test_registrar_devolucion_cantidad_cero():
    from models.devoluciones import registrar_devolucion
    ok, msg, dev_id = registrar_devolucion(1, 1, 1, 0, "motivo")
    assert ok is False
    assert "cantidad" in msg.lower()


def test_registrar_devolucion_cantidad_negativa():
    from models.devoluciones import registrar_devolucion
    ok, msg, dev_id = registrar_devolucion(1, 1, 1, -5, "motivo")
    assert ok is False


def test_registrar_devolucion_motivo_vacio():
    from models.devoluciones import registrar_devolucion
    ok, msg, dev_id = registrar_devolucion(1, 1, 1, 3, "")
    assert ok is False
    assert "motivo" in msg.lower()


def test_registrar_devolucion_motivo_espacios():
    from models.devoluciones import registrar_devolucion
    ok, msg, dev_id = registrar_devolucion(1, 1, 1, 3, "   ")
    assert ok is False


def test_registrar_devolucion_exitosa():
    with patch("models.devoluciones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.side_effect = [
            {"total": 5},    # _generar_numero_dev count
            {"id": 1}        # RETURNING id
        ]
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.devoluciones import registrar_devolucion
        ok, numero, dev_id = registrar_devolucion(1, 1, 1, 2, "Defectuoso")
        assert ok is True
        assert numero.startswith("DEV-")


# ── Tests listar_devoluciones ─────────────────────────────────────────────────

def test_listar_devoluciones_sin_filtros():
    with patch("models.devoluciones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.devoluciones import listar_devoluciones
        resultado = listar_devoluciones()
        assert isinstance(resultado, list)


def test_listar_devoluciones_por_estado():
    with patch("models.devoluciones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.devoluciones import listar_devoluciones
        resultado = listar_devoluciones(estado="Pendiente")
        assert isinstance(resultado, list)


def test_listar_devoluciones_por_proveedor():
    with patch("models.devoluciones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.devoluciones import listar_devoluciones
        resultado = listar_devoluciones(proveedor_id=1)
        assert isinstance(resultado, list)


def test_listar_devoluciones_ambos_filtros():
    with patch("models.devoluciones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.devoluciones import listar_devoluciones
        resultado = listar_devoluciones(estado="Procesada", proveedor_id=2)
        assert isinstance(resultado, list)


# ── Tests actualizar_estado_devolucion ────────────────────────────────────────

def test_actualizar_estado_devolucion_invalido():
    from models.devoluciones import actualizar_estado_devolucion
    ok, msg = actualizar_estado_devolucion(1, "EstadoMalo")
    assert ok is False


def test_actualizar_estado_devolucion_procesada():
    with patch("models.devoluciones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.devoluciones import actualizar_estado_devolucion
        ok, msg = actualizar_estado_devolucion(1, "Procesada")
        assert ok is True


def test_actualizar_estado_devolucion_rechazada():
    with patch("models.devoluciones.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.devoluciones import actualizar_estado_devolucion
        ok, msg = actualizar_estado_devolucion(1, "Rechazada")
        assert ok is True
