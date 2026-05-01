"""
AutoParts Express - Punto de entrada principal (Sprint 3)
Ejecutar desde la carpeta autoparts/:
    python main.py

Flujo de arranque:
  1. App llama a _check_db() para verificar la conexión a PostgreSQL
  2. Si la BD no está disponible, muestra error y termina
  3. Si todo está bien, muestra la ventana de login
  4. Tras autenticación exitosa, muestra la ventana principal
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from utils.styles import APP_STYLE

# Tarea completada: integración de BD verificada en _check_db()
_APP_NAME = "AutoParts Express"


class App(QApplication):
    """
    Subclase de QApplication que centraliza la inicialización y
    el flujo de navegación entre ventanas (login ↔ ventana principal).
    """

    def __init__(self, argv):
        super().__init__(argv)

        self.setApplicationName(_APP_NAME)
        self.setOrganizationName(_APP_NAME)
        self.setStyleSheet(APP_STYLE)
        self.setFont(QFont("Segoe UI", 12))

        self._login_window = None
        self._main_window = None

        if not self._check_db():
            QMessageBox.critical(
                None,
                "Error de conexión",
                "No se pudo conectar a la base de datos.\n"
                "Verifica que PostgreSQL esté corriendo y que\n"
                "las variables de entorno DB_* estén configuradas."
            )
            sys.exit(1)

        self._show_login()

    def _show_login(self):
        """Cierra la ventana principal (si existe) y muestra la ventana de login."""
        from ui.login import LoginWindow

        if self._main_window:
            self._main_window.close()
            self._main_window = None

        self._login_window = LoginWindow(on_success=self._handle_login_success)
        self._login_window.resize(900, 620)
        self._login_window.show()

    def _handle_login_success(self, usuario):
        """Callback que se ejecuta cuando el login es exitoso."""
        from ui.main_window import MainWindow

        if self._login_window:
            self._login_window.close()
            self._login_window = None

        self._main_window = MainWindow(on_logout=self._show_login)
        self._main_window.showMaximized()

    def _check_db(self) -> bool:
        """Verifica que la base de datos sea accesible antes de arrancar."""
        try:
            from db.connection import test_connection
            return test_connection()
        except Exception:
            return False


def main():
    """Función principal: crea la instancia de App y entra al event loop de Qt."""
    app = App(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
