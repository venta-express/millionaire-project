"""Tests unitarios para models/reportes.py"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date


def _mock_ctx_factory(rows_list):
    """Helper que crea un mock de db_cursor que retorna multiples resultados."""
    mock_ctx = MagicMock()
    mock_cur = MagicMock()
    mock_cur.fetchone.side_effect = rows_list[:1] if rows_list else [None]
    mock_cur.fetchall.return_value = rows_list[1:] if len(rows_list) > 1 else []
    mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
    mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
    return mock_ctx, mock_cur


def test_reporte_ventas_mock():
    """reporte_ventas debe retornar dict con claves esperadas."""
    resumen_row = {
        "total_ventas": 10, "ingresos_totales": 500000.0,
        "descuentos_totales": 0.0, "ticket_promedio": 50000.0
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
        assert "por_dia" in resultado
        assert "productos_top" in resultado
        assert "por_metodo_pago" in resultado


def test_reporte_inventario_mock():
    """reporte_inventario debe retornar dict con resumen y productos."""
    resumen_row = {
        "total_productos": 50, "valor_total": 5000000.0,
        "con_stock_bajo": 3, "sin_stock": 1
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


def test_reporte_por_vendedor_mock():
    """reporte_por_vendedor debe retornar dict con datos de vendedores."""
    resumen_row = {
        "total_ventas": 5, "ingresos_totales": 250000.0,
        "descuentos_totales": 0.0, "ticket_promedio": 50000.0
    }
    with patch("models.reportes.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = resumen_row
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.reportes import reporte_por_vendedor
        resultado = reporte_por_vendedor(date(2026, 1, 1), date(2026, 12, 31))
        assert isinstance(resultado, dict)


def test_reporte_por_vendedor_con_id_mock():
    """reporte_por_vendedor con vendedor_id especifico."""
    resumen_row = {
        "total_ventas": 3, "ingresos_totales": 150000.0,
        "descuentos_totales": 0.0, "ticket_promedio": 50000.0
    }
    with patch("models.reportes.db_cursor") as mock_ctx:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = resumen_row
        mock_cur.fetchall.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)
        from models.reportes import reporte_por_vendedor
        resultado = reporte_por_vendedor(date(2026, 1, 1), date(2026, 12, 31), vendedor_id=1)
        assert isinstance(resultado, dict)


def test_constantes_reportes():
    """Las constantes del modulo deben tener valores correctos."""
    from models.reportes import TITULO_AUTOPARTS, TITULO_VENTAS
    assert TITULO_AUTOPARTS == "AutoParts Express"
    assert TITULO_VENTAS == "Total Ventas"
