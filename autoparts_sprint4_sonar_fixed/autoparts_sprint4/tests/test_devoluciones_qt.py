"""
AutoParts Express - Pruebas Gráficas con pytest-qt
"""

import pytest
import sys
import os
from datetime import datetime

# IMPORTANTE: Cargar variables de entorno ANTES de cualquier import de db
from dotenv import load_dotenv
load_dotenv()

# Verificar que la contraseña se cargó
print(f"DB_PASSWORD cargada: {'OK' if os.getenv('DB_PASSWORD') else 'NO'}")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton, QComboBox, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from models.inventario import registrar_producto, buscar_productos
from models.auth import iniciar_sesion


@pytest.fixture
def app(qtbot):
    """Prepara la aplicación para pruebas"""
    from ui.main_window import MainWindow
    
    # Login
    ok, msg, usuario = iniciar_sesion('admin', 'admin123')
    if not ok:
        print(f"Error de login: {msg}")
    assert ok == True, f"Login falló: {msg}"
    
    # Ventana principal
    window = MainWindow(lambda: None)
    window.show()
    qtbot.addWidget(window)
    
    return window, qtbot, usuario


class TestDevoluciones:
    
    def test_abrir_devoluciones(self, app):
        """Prueba 1: Abrir el módulo Devoluciones"""
        window, qtbot, usuario = app
        
        # Buscar botón Devoluciones en el sidebar
        botones = window.findChildren(QPushButton, "btn_nav")
        btn_devoluciones = None
        
        for btn in botones:
            if "Devoluciones" in btn.text():
                btn_devoluciones = btn
                break
        
        assert btn_devoluciones is not None, "No se encontró el botón Devoluciones"
        
        # Hacer clic
        qtbot.mouseClick(btn_devoluciones, Qt.LeftButton)
        QTest.qWait(1000)
        
        print("✅ Módulo Devoluciones abierto")
    
    def test_abrir_dialogo_nueva_devolucion(self, app):
        """Prueba 2: Abrir el diálogo Nueva Devolución"""
        window, qtbot, usuario = app
        
        # Ir a Devoluciones
        for btn in window.findChildren(QPushButton, "btn_nav"):
            if "Devoluciones" in btn.text():
                qtbot.mouseClick(btn, Qt.LeftButton)
                break
        
        QTest.qWait(500)
        
        # Buscar botón "Nueva Devolución"
        btn_nueva = window.findChild(QPushButton, "btn_primary")
        assert btn_nueva is not None, "No se encontró el botón Nueva Devolución"
        
        qtbot.mouseClick(btn_nueva, Qt.LeftButton)
        QTest.qWait(1000)
        
        print("✅ Diálogo Nueva Devolución abierto")
    
    def test_llenar_formulario_devolucion(self, app):
        """Prueba 3: Llenar formulario de devolución"""
        window, qtbot, usuario = app
        
        # Crear producto de prueba
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        codigo = f"TEST-{timestamp}"
        
        ok, msg = registrar_producto(
            codigo=codigo,
            nombre=f"Producto Test {timestamp}",
            descripcion="Creado para prueba",
            categoria_id=1,
            precio=50000,
            stock_inicial=100,
            stock_minimo=10
        )
        assert ok, f"Error al crear producto: {msg}"
        print(f"✅ Producto creado: {codigo}")
        
        # Navegar a Devoluciones
        for btn in window.findChildren(QPushButton, "btn_nav"):
            if "Devoluciones" in btn.text():
                qtbot.mouseClick(btn, Qt.LeftButton)
                break
        
        QTest.qWait(500)
        
        # Abrir Nueva Devolución
        btn_nueva = window.findChild(QPushButton, "btn_primary")
        qtbot.mouseClick(btn_nueva, Qt.LeftButton)
        QTest.qWait(1000)
        
        # Encontrar el diálogo
        dialogo = None
        for w in QApplication.topLevelWidgets():
            if "Nueva Devolución" in w.windowTitle():
                dialogo = w
                break
        
        assert dialogo is not None, "No se encontró el diálogo"
        
        # Buscar widgets dentro del diálogo
        combos = dialogo.findChildren(QComboBox)
        inputs = dialogo.findChildren(QLineEdit)
        textos = dialogo.findChildren(QTextEdit)
        
        proveedor_combo = combos[0] if combos else None
        producto_input = inputs[0] if inputs else None
        cantidad_input = inputs[1] if len(inputs) > 1 else None
        motivo_text = textos[0] if textos else None
        
        assert proveedor_combo is not None, "No se encontró combo proveedor"
        assert producto_input is not None, "No se encontró campo producto"
        assert motivo_text is not None, "No se encontró campo motivo"
        
        # Llenar formulario
        if proveedor_combo.count() > 0:
            proveedor_combo.setCurrentIndex(0)
        
        producto_input.setText(codigo)
        
        if cantidad_input:
            cantidad_input.setText("1")
        
        motivo_text.setPlainText(f"Prueba automática {timestamp}")
        
        # Buscar botón Registrar
        for btn in dialogo.findChildren(QPushButton):
            if "Registrar" in btn.text() or btn.objectName() == "btn_primary":
                qtbot.mouseClick(btn, Qt.LeftButton)
                break
        
        QTest.qWait(1500)
        
        print(f"✅ Devolución registrada para producto {codigo}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])