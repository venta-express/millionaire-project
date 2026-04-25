"""
Tests unitarios para models/reportes.py
Sprint 4: Cobertura de reportes, exportacion Excel y PDF,
          incluyendo caso fetchone=None.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import date
from models.reportes import (
    reporte_ventas, reporte_inventario, reporte_por_vendedor,
    exportar_excel, exportar_pdf,
)


def _make_ctx(cur=None):
    if cur is None:
        cur = MagicMock()
    ctx = MagicMock()
    ctx.return_value.__enter__ = MagicMock(return_value=cur)
    ctx.return_value.__exit__ = MagicMock(return_value=False)
    return cur, ctx


# â”€â”€ reporte_ventas â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_reporte_ventas_retorna_dict():
    resumen_row = {
        "total_ventas": 10, "ingresos_totales": 500000.0,
        "descuentos_totales": 5000.0, "ticket_promedio": 50000.0,
    }
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = resumen_row
    cur.fetchall.return_value = []
    with patch("models.reportes.db_cursor", ctx):
        resultado = reporte_ventas(date(2026, 1, 1), date(2026, 12, 31))
        assert isinstance(resultado, dict)
        assert "resumen" in resultado


def test_reporte_ventas_tiene_claves():
    resumen_row = {
        "total_ventas": 0, "ingresos_totales": 0.0,
        "descuentos_totales": 0.0, "ticket_promedio": 0.0,
    }
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = resumen_row
    cur.fetchall.return_value = []
    with patch("models.reportes.db_cursor", ctx):
        resultado = reporte_ventas(date(2026, 1, 1), date(2026, 1, 31))
        assert "por_dia" in resultado
        assert "productos_top" in resultado


def test_reporte_ventas_resumen_none():
    """Si fetchone retorna None (tabla vacia), el reporte no debe lanzar excepcion."""
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = None
    cur.fetchall.return_value = []
    with patch("models.reportes.db_cursor", ctx):
        try:
            resultado = reporte_ventas(date(2026, 1, 1), date(2026, 1, 31))
            assert isinstance(resultado, dict)
        except TypeError:
            pytest.fail("reporte_ventas lanza TypeError cuando fetchone retorna None")


# â”€â”€ reporte_inventario â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_reporte_inventario_retorna_dict():
    resumen_row = {
        "total_productos": 50, "productos_activos": 45,
        "total_categorias": 8, "valor_inventario": 2500000.0,
    }
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = resumen_row
    cur.fetchall.return_value = []
    with patch("models.reportes.db_cursor", ctx):
        resultado = reporte_inventario()
        assert isinstance(resultado, dict)


def test_reporte_inventario_tiene_claves():
    resumen_row = {
        "total_productos": 0, "productos_activos": 0,
        "total_categorias": 0, "valor_inventario": 0.0,
    }
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = resumen_row
    cur.fetchall.return_value = []
    with patch("models.reportes.db_cursor", ctx):
        resultado = reporte_inventario()
        assert "resumen" in resultado
        assert "productos" in resultado


def test_reporte_inventario_resumen_none():
    """Si fetchone retorna None, el reporte no debe lanzar excepcion."""
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = None
    cur.fetchall.return_value = []
    with patch("models.reportes.db_cursor", ctx):
        try:
            resultado = reporte_inventario()
            assert isinstance(resultado, dict)
        except TypeError:
            pytest.fail("reporte_inventario lanza TypeError cuando fetchone retorna None")


# â”€â”€ reporte_por_vendedor â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_reporte_por_vendedor_todos():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.reportes.db_cursor", ctx):
        resultado = reporte_por_vendedor(date(2026, 1, 1), date(2026, 12, 31))
        assert isinstance(resultado, dict)


def test_reporte_por_vendedor_especifico():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.reportes.db_cursor", ctx):
        resultado = reporte_por_vendedor(date(2026, 1, 1), date(2026, 12, 31), vendedor_id=1)
        assert isinstance(resultado, dict)


# â”€â”€ exportar_excel â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_exportar_excel_tipo_invalido():
    ok, msg = exportar_excel("tipo_invalido", {}, os.path.join(tempfile.gettempdir(), "test.xlsx"))
    assert ok is False


def test_exportar_excel_ventas():
    datos = {
        "resumen": {
            "total_ventas": 5, "ingresos_totales": 250000.0,
            "descuentos_totales": 0.0, "ticket_promedio": 50000.0,
        },
        "por_dia": [],
        "productos_top": [],
        "por_metodo_pago": [],
        "por_vendedor": [],
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta = os.path.join(tmpdir, "reporte.xlsx")
        ok, msg = exportar_excel("ventas", datos, ruta)
        assert ok is True
        assert os.path.exists(ruta)


def test_exportar_excel_inventario():
    datos = {
        "resumen": {
            "total_productos": 10, "productos_activos": 9,
            "total_categorias": 3, "valor_inventario": 500000.0,
        },
        "productos": [],
        "stock_bajo": [],
        "por_categoria": [],
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta = os.path.join(tmpdir, "inventario.xlsx")
        ok, msg = exportar_excel("inventario", datos, ruta)
        assert ok is True


def test_exportar_excel_vendedor():
    datos = {"vendedores": [], "detalle": []}
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta = os.path.join(tmpdir, "vendedor.xlsx")
        ok, msg = exportar_excel("vendedor", datos, ruta)
        assert ok is True


# â”€â”€ exportar_pdf â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def test_exportar_pdf_tipo_invalido():
    ok, msg = exportar_pdf("tipo_malo", {}, os.path.join(tempfile.gettempdir(), "test.pdf"))
    assert ok is False


def test_exportar_pdf_ventas():
    datos = {
        "resumen": {
            "total_ventas": 3, "ingresos_totales": 150000.0,
            "descuentos_totales": 0.0, "ticket_promedio": 50000.0,
        },
        "por_dia": [],
        "productos_top": [],
        "por_metodo_pago": [],
        "por_vendedor": [],
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta = os.path.join(tmpdir, "reporte.pdf")
        ok, msg = exportar_pdf("ventas", datos, ruta)
        assert ok is True
        assert os.path.exists(ruta)


def test_exportar_pdf_inventario():
    datos = {
        "resumen": {
            "total_productos": 5, "productos_activos": 4,
            "total_categorias": 2, "valor_inventario": 200000.0,
        },
        "productos": [],
        "stock_bajo": [],
        "por_categoria": [],
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta = os.path.join(tmpdir, "inv.pdf")
        ok, msg = exportar_pdf("inventario", datos, ruta)
        assert ok is True

