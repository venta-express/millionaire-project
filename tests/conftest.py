"""
AutoParts Express - Configuracion de pytest
Sprint 4: Tests unitarios para aumentar cobertura en SonarCloud.
"""

import pytest
import sys
import os
from unittest.mock import MagicMock

# Agregar el directorio raiz al path para importar modulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockCursor:
    """Cursor simulado para tests sin base de datos real."""
    def __init__(self, rows=None):
        self._rows = rows or []
        self.executed = []
        self.committed = False
        self._fetchone_val = self._rows[0] if self._rows else None

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def fetchone(self):
        return self._fetchone_val

    def fetchall(self):
        return self._rows

    def set_fetchone(self, val):
        self._fetchone_val = val

    def __iter__(self):
        return iter(self._rows)


class MockConnection:
    """Conexion simulada para tests."""
    def __init__(self):
        self.cursor_obj = MockCursor()
        self.rolled_back = False

    def cursor(self, cursor_factory=None):
        return self.cursor_obj

    def commit(self):
        self.cursor_obj.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        pass


@pytest.fixture
def mock_cursor():
    return MockCursor()


@pytest.fixture
def mock_connection():
    return MockConnection()


@pytest.fixture
def make_db_ctx():
    """
    Fixture factory: devuelve una funcion que construye un par (cur, ctx)
    listo para usar como patch target de db_cursor.

    Uso:
        def test_algo(make_db_ctx):
            cur, ctx = make_db_ctx()
            with patch("models.xxx.db_cursor", ctx):
                ...
    """
    def _factory(rows=None, fetchone_val=None):
        cur = MagicMock()
        if rows is not None:
            cur.fetchall.return_value = rows
        if fetchone_val is not None:
            cur.fetchone.return_value = fetchone_val
        ctx = MagicMock()
        ctx.return_value.__enter__ = MagicMock(return_value=cur)
        ctx.return_value.__exit__ = MagicMock(return_value=False)
        return cur, ctx
    return _factory
