"""
Tests unitarios para models/reportes.py
Sprint 4: Cobertura de reportes, exportacion Excel y PDF.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import date


# ── Tests reporte_ventas ──────────────────────────────────────────────────────

def test_reporte_ventas_retorna_dict():
    resumen_row = {
        "total_ventas": 10, "ingresos_totales": 500000.0,
        "descuentos_totales": 5000.0, "ticket_promedio": 50000.0
    }
    with patch("models.reportes.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = resumen_row
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.reportes import reporte_ventas
        resultado = reporte_ventas(date(2026, 1, 1), date(2026, 12, 31))
        assert isinstance(resultado, dict)
        assert "resumen" in resultado


def test_reporte_ventas_tiene_claves():
    resumen_row = {
        "total_ventas": 0, "ingresos_totales": 0.0,
        "descuentos_totales": 0.0, "ticket_promedio": 0.0
    }
    with patch("models.reportes.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = resumen_row
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.reportes import reporte_ventas
        resultado = reporte_ventas(date(2026, 1, 1), date(2026, 1, 31))
        assert "por_dia" in resultado
        assert "productos_top" in resultado


# ── Tests reporte_inventario ──────────────────────────────────────────────────

def test_reporte_inventario_retorna_dict():
    resumen_row = {
        "total_productos": 50, "productos_activos": 45,
        "total_categorias": 8, "valor_inventario": 2500000.0
    }
    with patch("models.reportes.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = resumen_row
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.reportes import reporte_inventario
        resultado = reporte_inventario()
        assert isinstance(resultado, dict)


def test_reporte_inventario_tiene_claves():
    resumen_row = {
        "total_productos": 0, "productos_activos": 0,
        "total_categorias": 0, "valor_inventario": 0.0
    }
    with patch("models.reportes.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = resumen_row
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.reportes import reporte_inventario
        resultado = reporte_inventario()
        assert "resumen" in resultado
        assert "productos" in resultado


# ── Tests reporte_por_vendedor ────────────────────────────────────────────────

def test_reporte_por_vendedor_todos():
    with patch("models.reportes.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.reportes import reporte_por_vendedor
        resultado = reporte_por_vendedor(date(2026, 1, 1), date(2026, 12, 31))
        assert isinstance(resultado, dict)


def test_reporte_por_vendedor_especifico():
    with patch("models.reportes.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.reportes import reporte_por_vendedor
        resultado = reporte_por_vendedor(date(2026, 1, 1), date(2026, 12, 31), vendedor_id=1)
        assert isinstance(resultado, dict)


# ── Tests exportar_excel ──────────────────────────────────────────────────────

def test_exportar_excel_tipo_invalido():
    from models.reportes import exportar_excel
    ok, msg = exportar_excel("tipo_invalido", {}, "/tmp/test.xlsx")
    assert ok is False


def test_exportar_excel_ventas():
    datos = {
        "resumen": {
            "total_ventas": 5, "ingresos_totales": 250000.0,
            "descuentos_totales": 0.0, "ticket_promedio": 50000.0
        },
        "por_dia": [],
        "productos_top": [],
        "por_metodo_pago": [],
        "por_vendedor": []
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta = os.path.join(tmpdir, "reporte.xlsx")
        from models.reportes import exportar_excel
        ok, msg = exportar_excel("ventas", datos, ruta)
        assert ok is True
        assert os.path.exists(ruta)


def test_exportar_excel_inventario():
    datos = {
        "resumen": {
            "total_productos": 10, "productos_activos": 9,
            "total_categorias": 3, "valor_inventario": 500000.0
        },
        "productos": [],
        "stock_bajo": [],
        "por_categoria": []
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta = os.path.join(tmpdir, "inventario.xlsx")
        from models.reportes import exportar_excel
        ok, msg = exportar_excel("inventario", datos, ruta)
        assert ok is True


def test_exportar_excel_vendedor():
    datos = {
        "vendedores": [],
        "detalle": []
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta = os.path.join(tmpdir, "vendedor.xlsx")
        from models.reportes import exportar_excel
        ok, msg = exportar_excel("vendedor", datos, ruta)
        assert ok is True


# ── Tests exportar_pdf ────────────────────────────────────────────────────────

def test_exportar_pdf_tipo_invalido():
    from models.reportes import exportar_pdf
    ok, msg = exportar_pdf("tipo_malo", {}, "/tmp/test.pdf")
    assert ok is False


def test_exportar_pdf_ventas():
    datos = {
        "resumen": {
            "total_ventas": 3, "ingresos_totales": 150000.0,
            "descuentos_totales": 0.0, "ticket_promedio": 50000.0
        },
        "por_dia": [],
        "productos_top": [],
        "por_metodo_pago": [],
        "por_vendedor": []
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta = os.path.join(tmpdir, "reporte.pdf")
        from models.reportes import exportar_pdf
        ok, msg = exportar_pdf("ventas", datos, ruta)
        assert ok is True
        assert os.path.exists(ruta)


def test_exportar_pdf_inventario():
    datos = {
        "resumen": {
            "total_productos": 5, "productos_activos": 4,
            "total_categorias": 2, "valor_inventario": 200000.0
        },
        "productos": [],
        "stock_bajo": [],
        "por_categoria": []
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        ruta = os.path.join(tmpdir, "inv.pdf")
        from models.reportes import exportar_pdf
        ok, msg = exportar_pdf("inventario", datos, ruta)
        assert ok is True
