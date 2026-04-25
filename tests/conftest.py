"""
AutoParts Express - Configuracion de pytest
Sprint 4: Tests unitarios para aumentar cobertura en SonarCloud.
"""

import pytest
import sys
import os

# Agregar el directorio raiz al path para importar modulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockCursor:
    """Cursor simulado para tests sin base de datos real."""
    def __init__(self, rows=None):
        self._rows = rows or []
        self.executed = []
        self.committed = False

    def execute(self, sql, params=None):
        self.executed.append((sql, params))

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return self._rows

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
