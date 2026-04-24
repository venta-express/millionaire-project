"""
AutoParts Express - Punto de entrada principal (Sprint 2)
Ejecutar desde la carpeta autoparts/:
    python main.py

Flujo de arranque:
  1. Se crea la instancia de App (subclase de QApplication)
  2. App llama a _check_db() para verificar la conexión a PostgreSQL
  3. Si la BD no está disponible, muestra error y termina
  4. Si todo está bien, muestra la ventana de login
  5. Tras autenticación exitosa, muestra la ventana principal
"""

# sys: para pasar argv a QApplication y para sys.exit()
import sys

# os: para manipular rutas de forma portátil
import os

# Agregamos el directorio raíz al path de Python para que los imports
# de 'db', 'models', 'ui' y 'utils' funcionen correctamente sin importar
# desde qué directorio se ejecute el script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports de PySide6: la clase base de la aplicación Qt
from PySide6.QtWidgets import QApplication, QMessageBox

# QFont: tipografía por defecto de toda la aplicación
from PySide6.QtGui import QFont

# Qt: constantes de alineación y comportamiento
from PySide6.QtCore import Qt

# Importamos el stylesheet global (colores, botones, tablas, etc.)
from utils.styles import APP_STYLE


class App(QApplication):
    """
    Subclase de QApplication que centraliza la inicialización y
    el flujo de navegación entre ventanas (login ↔ ventana principal).
    """

    def __init__(self, argv):
        """
        Constructor: configura la app y arranca el flujo de login.
        Parámetros:
            argv: argumentos de línea de comandos (sys.argv)
        """
        super().__init__(argv)

        # Metadatos de la aplicación (usados por el SO y algunos diálogos)
        self.setApplicationName("AutoParts Express")
        self.setOrganizationName("AutoParts Express")

        # Aplicamos el stylesheet global definido en utils/styles.py
        self.setStyleSheet(APP_STYLE)

        # Tipografía por defecto para todos los widgets de la app
        self.setFont(QFont("Segoe UI", 12))

        # Referencias a las ventanas activas (None cuando no están abiertas)
        self._login_window = None
        self._main_window = None

        # Verificamos la BD antes de mostrar cualquier ventana
        if not self._check_db():
            # Sin BD operativa no podemos continuar
            QMessageBox.critical(
                None,
                "Error de conexión",
                "No se pudo conectar a la base de datos.\n"
                "Verifica que PostgreSQL esté corriendo y que\n"
                "los datos de conexión en db/connection.py sean correctos."
            )
            sys.exit(1)  # Terminamos con código de error

        # Todo OK: mostramos la ventana de login
        self._show_login()

    def _show_login(self):
        """
        Cierra la ventana principal (si existe) y muestra la ventana de login.
        Es llamado también al hacer logout para regresar al inicio de sesión.
        """
        # Importación diferida para evitar importar PySide6 antes de la instancia QApplication
        from ui.login import LoginWindow

        # Si había una ventana principal abierta, la cerramos
        if self._main_window:
            self._main_window.close()
            self._main_window = None

        # Creamos la ventana de login pasando el callback de éxito
        self._login_window = LoginWindow(on_success=self._handle_login_success)
        self._login_window.resize(900, 620)  # Tamaño inicial de la ventana de login
        self._login_window.show()

    def _handle_login_success(self, usuario):
        """
        Callback que se ejecuta cuando el login es exitoso.
        Cierra el login y abre la ventana principal.
        Parámetros:
            usuario: objeto Usuario del modelo de autenticación
        """
        # Importación diferida de la ventana principal
        from ui.main_window import MainWindow

        # Cerramos la ventana de login
        if self._login_window:
            self._login_window.close()
            self._login_window = None

        # Creamos la ventana principal con el callback de logout
        self._main_window = MainWindow(on_logout=self._show_login)

        # showMaximized() abre la ventana en pantalla completa (sin bordes de OS)
        self._main_window.showMaximized()

    def _check_db(self) -> bool:
        """
        Verifica que la base de datos sea accesible antes de arrancar.
        Retorna True si la conexión funciona, False en caso contrario.
        """
        try:
            from db.connection import test_connection
            return test_connection()  # Ejecuta SELECT 1 para probar conectividad
        except Exception:
            return False  # Cualquier error de importación o conexión → False


def main():
    """
    Función principal: crea la instancia de App y entra al event loop de Qt.
    sys.exit() asegura que el código de salida de Qt se propague al SO.
    """
    app = App(sys.argv)   # Creamos la aplicación (arranca el flujo)
    sys.exit(app.exec())  # app.exec() bloquea hasta que la app se cierra


# ── Punto de entrada estándar de Python ──────────────────────────────────────
# Este bloque solo se ejecuta si el archivo se corre directamente (no al importarlo)
if __name__ == "__main__":
    main()
