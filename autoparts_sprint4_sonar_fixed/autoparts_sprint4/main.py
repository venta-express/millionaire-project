"""
AutoParts Express - Punto de entrada principal (Sprint 4)
Ejecutar desde la carpeta autoparts_sprint4/:
    python main.py

Flujo de arranque:
  1. Carga variables de entorno desde .env si existe
  2. Verifica conexion a PostgreSQL
  3. Inicializa el schema de BD (acumulativo Sprint 1-4)
  4. Muestra ventana de login
  5. Tras autenticacion exitosa, muestra ventana principal
"""

import sys
import os

# Cargar .env si existe
def _cargar_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if linea and not linea.startswith("#") and "=" in linea:
                    clave, _, valor = linea.partition("=")
                    os.environ.setdefault(clave.strip(), valor.strip())

_cargar_env()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from utils.styles import APP_STYLE

_APP_NAME = "AutoParts Express"


class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName(_APP_NAME)
        self.setOrganizationName(_APP_NAME)
        self.setStyleSheet(APP_STYLE)
        self.setFont(QFont("Segoe UI", 12))

        self._login_window = None
        self._main_window  = None

        if not self._check_db():
            QMessageBox.critical(
                None,
                "Error de conexion",
                "No se pudo conectar a la base de datos.\n"
                "Verifica que PostgreSQL este corriendo y que\n"
                "las variables de entorno DB_* esten configuradas.\n\n"
                "Ejemplo de .env:\n"
                "DB_HOST=localhost\n"
                "DB_PORT=5432\n"
                "DB_NAME=autoparts_db\n"
                "DB_USER=postgres\n"
                "DB_PASS=tu_contrasena"
            )
            sys.exit(1)

        self._init_schema()
        self._show_login()

    def _check_db(self) -> bool:
        try:
            from db.connection import test_connection
            return test_connection()
        except Exception:
            return False

    def _init_schema(self):
        try:
            from db.connection import init_db
            init_db()
        except Exception as e:
            print(f"Advertencia al inicializar schema: {e}")

    def _show_login(self):
        from ui.login import LoginWindow
        if self._main_window:
            self._main_window.close()
            self._main_window = None
        self._login_window = LoginWindow(on_success=self._handle_login_success)
        self._login_window.resize(900, 620)
        self._login_window.show()

    def _handle_login_success(self, usuario):
        from ui.main_window import MainWindow
        if self._login_window:
            self._login_window.close()
            self._login_window = None
        self._main_window = MainWindow(on_logout=self._show_login)
        self._main_window.showMaximized()


def main():
    app = App(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
