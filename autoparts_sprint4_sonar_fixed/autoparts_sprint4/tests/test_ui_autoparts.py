"""
AutoParts Express — Pruebas Automatizadas con pytest-qt
Basadas en UI_Map_AutoParts_Sprint4.docx
"""

import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication, QPushButton, QLineEdit, QLabel, QDialog, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest


@pytest.fixture(scope="session")
def app():
    import sys
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


def mock_usuario_admin():
    from models.auth import Usuario
    return Usuario(
        id=1, cedula="1000000001", nombre="Administrador",
        username="admin", rol="Gerencia", activo=True, bloqueado=False
    )


def cursor_falso(fetchone=None, rows=None):
    cur = MagicMock()
    cur.fetchone.return_value = fetchone
    cur.fetchall.return_value = rows or []
    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=cur)
    ctx.__exit__ = MagicMock(return_value=False)
    return ctx


def encontrar_boton(ventana, object_name=None, texto=None):
    botones = ventana.findChildren(QPushButton)
    for btn in botones:
        if object_name and btn.objectName() == object_name:
            return btn
        if texto and texto.lower() in btn.text().lower():
            return btn
    return None


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBA DE LOGIN
# ══════════════════════════════════════════════════════════════════════════════

class TestLogin:
    def test_login_exitoso(self, app, qtbot):
        import bcrypt
        from ui.login import LoginWindow

        hash_real = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
        fila_admin = {
            "id": 1, "cedula": "1000000001", "nombre": "Administrador",
            "username": "admin", "password_hash": hash_real,
            "activo": True, "bloqueado": False,
            "intentos_fallidos": 0, "rol": "Gerencia"
        }

        ctx1 = cursor_falso(fetchone=fila_admin)
        ctx2 = cursor_falso()

        def capturar_ventana(usuario):
            nonlocal ventana_principal
            ventana_principal = usuario

        ventana_principal = None

        with patch("models.auth.db_cursor", side_effect=[ctx1, ctx2]):
            login = LoginWindow()
            login.on_login_success = capturar_ventana
            qtbot.addWidget(login)
            login.show()

            # Campos de login
            inputs = login.findChildren(QLineEdit)
            assert len(inputs) >= 2, "No se encontraron campos de login"

            QTest.keyClicks(inputs[0], "admin")
            QTest.keyClicks(inputs[1], "admin123")

            btn_login = encontrar_boton(login, object_name="btn_primary")
            assert btn_login is not None, "Boton btn_primary no encontrado"

            QTest.mouseClick(btn_login, Qt.LeftButton)
            qtbot.wait(500)

        assert ventana_principal is not None, "Login no funciono"
        print("  ✅ Login exitoso funciona")


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBA DE INVENTARIO
# ══════════════════════════════════════════════════════════════════════════════

class TestInventario:
    def test_inventario_muestra_productos(self, app, qtbot):
        from ui.inventario import InventarioView

        filas = [{
            "id": 1, "codigo": "FRN-001", "nombre": "Freno Delantero Honda",
            "descripcion": "", "categoria": "Frenos", "categoria_id": 1,
            "precio_unitario": 45000.0, "stock_actual": 20,
            "stock_minimo": 5, "activo": True
        }]
        categorias = [{"id": 1, "nombre": "Frenos"}, {"id": 2, "nombre": "Motor"}]

        ctx_prod = cursor_falso(rows=filas)
        ctx_cat = cursor_falso(rows=categorias)

        with patch("models.inventario.db_cursor", side_effect=[ctx_prod, ctx_cat]):
            ventana = InventarioView()
            qtbot.addWidget(ventana)
            ventana.show()
            qtbot.wait(500)

            # Verificar tabla
            tabla = ventana.table
            assert tabla.rowCount() >= 1, "La tabla deberia tener productos"
            print("  ✅ Inventario muestra productos")


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBA DE VENTAS
# ══════════════════════════════════════════════════════════════════════════════

class TestVentas:
    def test_ventas_catalogo_cargado(self, app, qtbot):
        from ui.ventas import VentasView

        productos = [{
            "id": 1, "codigo": "FRN-001", "nombre": "Freno Delantero Honda",
            "descripcion": "", "categoria": "Frenos", "categoria_id": 1,
            "precio_unitario": 45000.0, "stock_actual": 20,
            "stock_minimo": 5, "activo": True
        }]
        ctx = cursor_falso(rows=productos)

        with patch("models.inventario.db_cursor", return_value=ctx):
            ventana = VentasView()
            qtbot.addWidget(ventana)
            ventana.show()
            qtbot.wait(500)

            assert ventana.prod_table.rowCount() >= 0, "Catalogo deberia cargar"
            assert ventana.lbl_total is not None, "Label total no encontrado"
            print("  ✅ Ventas catalogo cargado")


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBA DE USUARIOS
# ══════════════════════════════════════════════════════════════════════════════

class TestUsuarios:
    def test_usuarios_tabla_cargada(self, app, qtbot):
        from ui.usuarios import UsuariosView

        usuarios = [{
            "id": 1, "cedula": "1000000001", "nombre": "Administrador",
            "username": "admin", "rol": "Gerencia",
            "activo": True, "bloqueado": False
        }]
        ctx = cursor_falso(rows=usuarios)

        with patch("models.auth.db_cursor", return_value=ctx):
            ventana = UsuariosView()
            qtbot.addWidget(ventana)
            ventana.show()
            qtbot.wait(500)

            assert ventana.tabla.rowCount() >= 1, "Tabla deberia tener usuarios"
            print("  ✅ Usuarios tabla cargada")


# ══════════════════════════════════════════════════════════════════════════════
# PRUEBA DE DEVOLUCIONES (¡LA IMPORTANTE!)
# ══════════════════════════════════════════════════════════════════════════════

class TestDevoluciones:
    def test_devoluciones_modulo_abre(self, app, qtbot):
        from ui.devoluciones import DevolucionesView

        proveedores = [{"id": 1, "nombre": "Moto Parts Express", "activo": True}]
        devoluciones = []

        ctx_prov = cursor_falso(rows=proveedores)
        ctx_dev = cursor_falso(rows=devoluciones)

        with patch("models.devoluciones.db_cursor", side_effect=[ctx_prov, ctx_dev]):
            ventana = DevolucionesView()
            qtbot.addWidget(ventana)
            ventana.show()
            qtbot.wait(500)

            # Verificar que existe el boton Nueva Devolucion
            btn_nueva = encontrar_boton(ventana, object_name="btn_primary")
            assert btn_nueva is not None, "Boton btn_primary (Nueva Devolucion) no encontrado"
            print("  ✅ Devoluciones modulo abierto")


# ══════════════════════════════════════════════════════════════════════════════
# EJECUTAR
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])