import pyautogui
import time
import pygetwindow as gw

print('=' * 60)
print('SCRIPT PARA OBTENER COORDENADAS EXACTAS')
print('=' * 60)

print('''
PASOS:
1. Abre la app MANUALMENTE en otra ventana: python main.py
2. Login con admin / admin123  
3. Navega a: Devoluciones → Nueva Devolución
4. Vas a ver el formulario (Proveedor, Producto, Cantidad, Motivo)
''')

input('Presiona ENTER cuando estés en el formulario de Devolución...')

v = None
for w in gw.getAllWindows():
    if 'autoparts' in w.title.lower() or 'express' in w.title.lower():
        v = w
        break

if not v:
    print('No se encontró la ventana de AutoParts')
    exit()

print(f'\nVentana detectada: left={v.left}, top={v.top}')
print('\n' + '=' * 60)
print('Coloca el MOUSE sobre cada campo y presiona ENTER')
print('=' * 60)

def get_coord(nombre):
    input(f'\nColoca el mouse en el campo "{nombre}" y presiona ENTER...')
    x, y = pyautogui.position()
    rel_x = x - v.left
    rel_y = y - v.top
    print(f'   {nombre}: X_rel={rel_x}, Y_rel={rel_y}')
    return rel_x, rel_y

print('\n')
coords = {}
for campo in ['PROVEEDOR', 'PRODUCTO', 'CANTIDAD', 'MOTIVO', 'BOTON REGISTRAR']:
    rx, ry = get_coord(campo)
    coords[campo] = (rx, ry)

print('\n' + '=' * 60)
print('COORDENADAS EXACTAS PARA TU PANTALLA:')
print('=' * 60)
for campo, (x, y) in coords.items():
    print(f'   {campo}: X_rel={x}, Y_rel={y}')
print('=' * 60)