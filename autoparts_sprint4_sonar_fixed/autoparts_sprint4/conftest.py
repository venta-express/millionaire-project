# conftest.py
# Archivo de configuración de pytest.
# Debe estar en la carpeta raíz del proyecto (donde está main.py),
# NO dentro de la carpeta tests/.
#
# Propósito: agrega la carpeta raíz al sys.path para que los imports
# como "from models.inventario import ..." funcionen correctamente
# al ejecutar pytest desde cualquier ubicación.

import sys
import os

# Insertamos la carpeta que contiene este archivo (la raíz del proyecto)
# al inicio del path de búsqueda de módulos de Python.
sys.path.insert(0, os.path.dirname(__file__))
