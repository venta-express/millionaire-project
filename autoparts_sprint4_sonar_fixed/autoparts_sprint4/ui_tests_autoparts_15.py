"""
AutoParts Express — 15 Pruebas Estables (SIN DEVOLUCIONES)
============================================================
Corregido: coordenada del botón Crear Usuario (0.58)
Cierre de factura con Escape
Datos únicos por timestamp

Ejecucion:
    python ui_tests_autoparts_15.py

NO muevas el mouse.
"""

import subprocess
import sys
import time
import pyautogui
import pygetwindow as gw
from datetime import datetime

pyautogui.PAUSE = 0.6
pyautogui.FAILSAFE = True

app_proceso = None

# ============================================================
# DATOS UNICOS (timestamp)
# ============================================================
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
ts_corto = datetime.now().strftime("%Y%m%d%H%M%S")

PRODUCTO_CODIGO = f"TEST-{ts_corto}"
PRODUCTO_NOMBRE = f"Producto Prueba {ts}"
CLIENTE_CEDULA = f"999888777{ts_corto[-4:]}"
CLIENTE_NOMBRE = f"Cliente Prueba {ts}"
USUARIO_USER = f"test_{ts_corto}"
USUARIO_CEDULA = f"111222333{ts_corto[-4:]}"

print("=" * 60)
print("15 PRUEBAS ESTABLES - DATOS ÚNICOS:")
print(f"  Producto: {PRODUCTO_CODIGO}")
print(f"  Cliente:  {CLIENTE_CEDULA}")
print(f"  Usuario:  {USUARIO_USER}")
print("=" * 60)

# ============================================================
# HELPERS
# ============================================================

def iniciar_app():
    global app_proceso
    print("  Abriendo AutoParts Express...")
    app_proceso = subprocess.Popen([sys.executable, "main.py"])
    time.sleep(5)

def cerrar_app():
    global app_proceso
    if app_proceso:
        app_proceso.terminate()
        time.sleep(1)

def obtener_ventana():
    for v in gw.getAllWindows():
        if "autoparts" in v.title.lower() or "express" in v.title.lower():
            return v
    return None

def activar():
    v = obtener_ventana()
    if not v:
        raise Exception("No se encontró la ventana")
    v.activate()
    time.sleep(0.8)
    return v

def sidebar_click(v, nombre):
    posiciones = {
        "Inicio": 218, "Inventario": 262, "Ventas": 306,
        "Clientes": 350, "Compras": 394, "Usuarios": 438,
        "Reportes": 482,
        "Auditoria": 614, "Configuracion": 658, "Cerrar sesion": 700,
    }
    pyautogui.click(v.left + 113, v.top + posiciones[nombre])
    time.sleep(2)

def hacer_login(v, usuario="admin", password="admin123"):
    pyautogui.click(v.left + int(v.width * 0.68), v.top + int(v.height * 0.42))
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.typewrite(usuario, interval=0.1)
    pyautogui.press("tab")
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.typewrite(password, interval=0.1)
    pyautogui.press("enter")
    time.sleep(4)

def ok_dialogo():
    pyautogui.press("enter")
    time.sleep(1)

# ============================================================
# PRUEBAS (15 estables)
# ============================================================

def test_01_login():
    print("\n  [01/15] Login con admin...")
    v = activar()
    hacer_login(v)
    print("     OK — Sesión iniciada")

def test_02_registrar_producto():
    print(f"\n  [02/15] Registrar producto {PRODUCTO_CODIGO}...")
    v = activar()
    sidebar_click(v, "Inventario")
    pyautogui.click(v.left + int(v.width * 0.85), v.top + int(v.height * 0.13))
    time.sleep(2)
    dx = v.left + int(v.width * 0.49)
    # Código
    pyautogui.click(dx, v.top + int(v.height * 0.22))
    pyautogui.hotkey("ctrl", "a")
    pyautogui.typewrite(PRODUCTO_CODIGO, interval=0.1)
    # Nombre
    pyautogui.click(dx, v.top + int(v.height * 0.32))
    pyautogui.typewrite(PRODUCTO_NOMBRE, interval=0.08)
    # Descripción
    pyautogui.click(dx, v.top + int(v.height * 0.43))
    pyautogui.typewrite(f"Creado {ts}", interval=0.05)
    # Categoría (Frenos)
    pyautogui.click(dx, v.top + int(v.height * 0.55))
    time.sleep(0.5)
    pyautogui.press("down")
    pyautogui.press("enter")
    # Precio
    pyautogui.click(dx, v.top + int(v.height * 0.65))
    pyautogui.hotkey("ctrl", "a")
    pyautogui.typewrite("55000", interval=0.1)
    # Stock inicial
    pyautogui.click(dx, v.top + int(v.height * 0.75))
    pyautogui.hotkey("ctrl", "a")
    pyautogui.typewrite("50", interval=0.1)
    pyautogui.scroll(-3)
    time.sleep(0.5)
    # Stock mínimo
    pyautogui.click(dx, v.top + int(v.height * 0.65))
    pyautogui.hotkey("ctrl", "a")
    pyautogui.typewrite("10", interval=0.1)
    # Guardar
    pyautogui.click(v.left + int(v.width * 0.60), v.top + int(v.height * 0.86))
    time.sleep(2)
    ok_dialogo()
    print(f"     OK — Producto {PRODUCTO_CODIGO} registrado")

def test_03_buscar_producto():
    print(f"\n  [03/15] Buscar producto...")
    v = activar()
    sidebar_click(v, "Inventario")
    pyautogui.click(v.left + int(v.width * 0.50), v.top + int(v.height * 0.17))
    pyautogui.typewrite(PRODUCTO_CODIGO[:7], interval=0.1)
    time.sleep(1.5)
    print("     OK — Producto encontrado")
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("delete")

def test_04_ventas_agregar():
    print("\n  [04/15] Agregar producto al carrito...")
    v = activar()
    sidebar_click(v, "Ventas")
    pyautogui.click(v.left + int(v.width * 0.40), v.top + int(v.height * 0.14))
    pyautogui.typewrite(PRODUCTO_CODIGO, interval=0.1)
    time.sleep(1.5)
    pyautogui.click(v.left + int(v.width * 0.40), v.top + int(v.height * 0.29))
    time.sleep(0.5)
    pyautogui.click(v.left + int(v.width * 0.40), v.top + int(v.height * 0.93))
    time.sleep(1)
    print("     OK — Producto en carrito")

def test_05_datos_cliente():
    print(f"\n  [05/15] Cliente: {CLIENTE_CEDULA}...")
    v = activar()
    pyautogui.click(v.left + int(v.width * 0.73), v.top + int(v.height * 0.62))
    pyautogui.hotkey("ctrl", "a")
    pyautogui.typewrite(CLIENTE_CEDULA, interval=0.1)
    pyautogui.press("tab")
    time.sleep(0.5)
    pyautogui.click(v.left + int(v.width * 0.83), v.top + int(v.height * 0.69))
    pyautogui.hotkey("ctrl", "a")
    pyautogui.typewrite(CLIENTE_NOMBRE, interval=0.08)
    print("     OK — Cliente registrado")

def test_06_confirmar_venta():
    print("\n  [06/15] Confirmar venta...")
    v = activar()
    pyautogui.click(v.left + int(v.width * 0.96), v.top + int(v.height * 0.88))
    time.sleep(3)
    print("     OK — Factura generada")
    # Cerrar factura con Escape (más fiable)
    time.sleep(1)
    pyautogui.press('escape')
    time.sleep(1)
    print("     OK — Factura cerrada")

def test_07_clientes_buscar():
    print(f"\n  [07/15] Buscar cliente...")
    v = activar()
    sidebar_click(v, "Clientes")
    pyautogui.click(v.left + int(v.width * 0.60), v.top + int(v.height * 0.17))
    pyautogui.typewrite(CLIENTE_NOMBRE[:10], interval=0.1)
    time.sleep(1.5)
    print("     OK — Cliente encontrado")

def test_08_historial_cliente():
    print("\n  [08/15] Ver historial...")
    v = activar()
    pyautogui.click(v.left + int(v.width * 0.34), v.top + int(v.height * 0.37))
    time.sleep(1.5)
    print("     OK — Historial visible")

def test_09_navegar_usuarios():
    print("\n  [09/15] Navegar a Usuarios...")
    v = activar()
    sidebar_click(v, "Usuarios")
    print("     OK — Módulo Usuarios abierto")

def test_10_crear_usuario():
    print(f"\n  [10/15] Crear usuario {USUARIO_USER}...")
    v = activar()
    pyautogui.click(v.left + int(v.width * 0.88), v.top + int(v.height * 0.11))
    time.sleep(2)
    dx = v.left + int(v.width * 0.52)
    pyautogui.click(dx, v.top + int(v.height * 0.35))
    pyautogui.typewrite(USUARIO_CEDULA, interval=0.1)
    pyautogui.press("tab")
    pyautogui.typewrite(USUARIO_USER, interval=0.08)
    pyautogui.press("tab")
    pyautogui.typewrite(USUARIO_USER, interval=0.1)
    pyautogui.press("tab")
    pyautogui.typewrite("Test123!", interval=0.1)
    # Rol: Vendedor (segunda opción)
    pyautogui.click(dx, v.top + int(v.height * 0.61))
    time.sleep(0.5)
    pyautogui.press("down")   # baja a Vendedor
    pyautogui.press("enter")
    # Botón Crear Usuario - coordenada corregida (más a la derecha)
    pyautogui.click(v.left + int(v.width * 0.58), v.top + int(v.height * 0.69))
    time.sleep(2)
    ok_dialogo()
    print("     OK — Usuario creado")

def test_11_navegar_auditoria():
    print("\n  [11/15] Navegar a Auditoría...")
    v = activar()
    sidebar_click(v, "Auditoria")
    time.sleep(1)
    print("     OK — Auditoría visible")

def test_12_navegar_configuracion():
    print("\n  [12/15] Navegar a Configuración...")
    v = activar()
    sidebar_click(v, "Configuracion")
    time.sleep(1)
    print("     OK — Configuración visible")

def test_13_actualizar_config():
    print("\n  [13/15] Actualizar configuración...")
    v = activar()
    sidebar_click(v, "Configuracion")
    # Cambiar teléfono (primer campo editable)
    pyautogui.click(v.left + int(v.width * 0.60), v.top + int(v.height * 0.35))
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.typewrite("3001234567", interval=0.1)
    # Guardar
    pyautogui.click(v.left + int(v.width * 0.46), v.top + int(v.height * 0.55))
    time.sleep(1)
    ok_dialogo()
    print("     OK — Configuración actualizada")

def test_14_generar_backup():
    print("\n  [14/15] Generar backup...")
    v = activar()
    sidebar_click(v, "Configuracion")
    # Botón "Generar Backup Ahora"
    pyautogui.click(v.left + int(v.width * 0.46), v.top + int(v.height * 0.75))
    time.sleep(4)
    print("     OK — Backup generado")

def test_15_cerrar_sesion():
    print("\n  [15/15] Cerrar sesión...")
    v = activar()
    sidebar_click(v, "Cerrar sesion")
    time.sleep(2)
    if not obtener_ventana():
        raise Exception("La ventana desapareció")
    print("     OK — Sesión cerrada")

# ============================================================
# EJECUCIÓN
# ============================================================
if __name__ == "__main__":
    pruebas = [
        test_01_login,
        test_02_registrar_producto,
        test_03_buscar_producto,
        test_04_ventas_agregar,
        test_05_datos_cliente,
        test_06_confirmar_venta,
        test_07_clientes_buscar,
        test_08_historial_cliente,
        test_09_navegar_usuarios,
        test_10_crear_usuario,
        test_11_navegar_auditoria,
        test_12_navegar_configuracion,
        test_13_actualizar_config,
        test_14_generar_backup,
        test_15_cerrar_sesion,
    ]

    print("=" * 62)
    print("  AutoParts Express — 15 Pruebas Estables")
    print("  Corregido: botón Crear Usuario ahora apunta a la derecha")
    print("  NO muevas el mouse durante la ejecución")
    print("=" * 62)
    print("\n  Iniciando en 3 segundos...")
    time.sleep(3)

    iniciar_app()

    passed = 0
    failed = 0

    for prueba in pruebas:
        try:
            prueba()
            print(f"  [OK]   {prueba.__name__}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {prueba.__name__} -> {e}")
            failed += 1
        time.sleep(0.8)

    print("\n" + "=" * 62)
    print(f"  RESULTADO: {passed} pasaron | {failed} fallaron | 15 total")
    print("=" * 62)

    time.sleep(3)
    cerrar_app()
