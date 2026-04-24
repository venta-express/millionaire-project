"""
AutoParts Express - Punto de entrada principal
Ejecutar: python main.py
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from utils.styles import APP_STYLE


class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("AutoParts Express")
        self.setOrganizationName("AutoParts Express")
        self.setStyleSheet(APP_STYLE)
        self.setFont(QFont("Segoe UI", 12))

        self._login_window = None
        self._main_window = None
        self._show_login()

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

    def _check_db(self) -> bool:
        """Verifica conexión a BD antes de arrancar."""
        try:
            from db.connection import test_connection
            return test_connection()
        except Exception:
            return False


def main():
    app = App(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
