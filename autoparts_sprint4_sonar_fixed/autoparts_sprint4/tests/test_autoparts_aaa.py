"""
AutoParts Express - Pruebas Unitarias con Patrón AAA
=====================================================
Módulos cubiertos:
  - models/inventario.py  (registrar_producto, ajustar_stock, buscar_productos,
                            desactivar_producto, obtener_producto)
  - models/auth.py        (iniciar_sesion, hash_password, cerrar_sesion,
                            crear_usuario, get_usuario_activo)
  - models/ventas.py      (ItemVenta, buscar_clientes)

Patrón AAA (Arrange – Act – Assert):
  • ARRANGE: preparar datos de entrada y configurar los mocks necesarios
  • ACT:     invocar la función bajo prueba
  • ASSERT:  verificar que el resultado obtenido coincide con el esperado

Ejecución:
    pip install pytest
    pytest test_autoparts_aaa.py -v
"""

import unittest
from unittest.mock import patch, MagicMock, call
from dataclasses import fields


# ──────────────────────────────────────────────────────────────────────────────
# Helpers para construir mocks de fila de base de datos
# ──────────────────────────────────────────────────────────────────────────────

def _fila(**kwargs) -> MagicMock:
    """
    Crea un mock que se comporta como un RealDictRow de psycopg2.
    Soporta acceso por clave (row['campo']) y desempaque con dict(row).
    """
    mock = MagicMock()
    mock.__getitem__.side_effect = kwargs.__getitem__
    mock.keys.return_value = kwargs.keys()
    mock.__iter__.side_effect = kwargs.__iter__
    mock.items.return_value = kwargs.items()
    # dict(row) usa esto:
    mock.__class__ = dict
    mock.copy = lambda: dict(**kwargs)
    # Para **dict(row) en Producto(**dict(row)):
    mock._data = kwargs
    return mock


def _dict_row(**kwargs):
    """Retorna un objeto que dict() convierte correctamente (DictRow simulado)."""

    class _Row(dict):
        pass

    return _Row(kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# BLOQUE 1: models/inventario.py
# ──────────────────────────────────────────────────────────────────────────────

class TestRegistrarProducto(unittest.TestCase):
    """Pruebas para inventario.registrar_producto()"""

    # ------------------------------------------------------------------
    # Prueba 1 – campos vacíos deben retornar error sin tocar la BD
    # ------------------------------------------------------------------
    def test_codigo_vacio_retorna_error(self):
        # ARRANGE
        codigo    = ""          # código intencionalmente vacío
        nombre    = "Filtro de aceite"
        descripcion = "Filtro estándar"
        categoria_id = 1
        precio    = 15000.0
        stock_ini = 10
        stock_min = 2

        # ACT
        from models.inventario import registrar_producto
        exito, mensaje = registrar_producto(
            codigo, nombre, descripcion, categoria_id, precio, stock_ini, stock_min
        )

        # ASSERT
        self.assertFalse(exito, "Debe fallar cuando el código está vacío")
        self.assertIn("obligatorios", mensaje.lower(),
                      "El mensaje debe mencionar campos obligatorios")

    # ------------------------------------------------------------------
    # Prueba 2 – precio negativo debe retornar error
    # ------------------------------------------------------------------
    def test_precio_negativo_retorna_error(self):
        # ARRANGE
        codigo    = "FLT-001"
        nombre    = "Filtro"
        precio    = -500.0          # precio inválido

        # ACT
        from models.inventario import registrar_producto
        exito, mensaje = registrar_producto(
            codigo, nombre, "", 1, precio, 5, 1
        )

        # ASSERT
        self.assertFalse(exito)
        self.assertIn("negativo", mensaje.lower())

    # ------------------------------------------------------------------
    # Prueba 3 – stock negativo debe retornar error
    # ------------------------------------------------------------------
    def test_stock_negativo_retorna_error(self):
        # ARRANGE
        codigo      = "FLT-002"
        nombre      = "Filtro aire"
        stock_ini   = -1            # stock inválido
        stock_min   = 2

        # ACT
        from models.inventario import registrar_producto
        exito, mensaje = registrar_producto(
            codigo, nombre, "", 1, 10000.0, stock_ini, stock_min
        )

        # ASSERT
        self.assertFalse(exito)
        self.assertIn("negativo", mensaje.lower())

    # ------------------------------------------------------------------
    # Prueba 4 – inserción exitosa devuelve True y el ID generado
    # ------------------------------------------------------------------
    @patch("models.inventario.db_cursor")
    def test_registro_exitoso_retorna_id(self, mock_db):
        # ARRANGE
        cur = MagicMock()
        cur.fetchone.return_value = _dict_row(id=42)
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # ACT
        from models.inventario import registrar_producto
        exito, mensaje = registrar_producto(
            "FLT-003", "Filtro combustible", "Filtro estándar",
            2, 12000.0, 20, 5
        )

        # ASSERT
        self.assertTrue(exito, "Debe retornar True en inserción exitosa")
        self.assertIn("42", mensaje, "El mensaje debe incluir el ID generado (42)")

    # ------------------------------------------------------------------
    # Prueba 5 – código duplicado debe retornar mensaje amigable
    # ------------------------------------------------------------------
    @patch("models.inventario.db_cursor")
    def test_codigo_duplicado_retorna_mensaje_claro(self, mock_db):
        # ARRANGE
        cur = MagicMock()
        cur.execute.side_effect = Exception("unique constraint violated")
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # ACT
        from models.inventario import registrar_producto
        exito, mensaje = registrar_producto(
            "FLT-001", "Filtro", "", 1, 5000.0, 10, 2
        )

        # ASSERT
        self.assertFalse(exito)
        self.assertIn("FLT-001", mensaje, "El mensaje debe mencionar el código duplicado")


class TestAjustarStock(unittest.TestCase):
    """Pruebas para inventario.ajustar_stock()"""

    # ------------------------------------------------------------------
    # Prueba 6 – stock negativo no debe aceptarse
    # ------------------------------------------------------------------
    def test_cantidad_negativa_retorna_error(self):
        # ARRANGE
        pid            = 5
        nueva_cantidad = -3     # valor inválido

        # ACT
        from models.inventario import ajustar_stock
        exito, mensaje = ajustar_stock(pid, nueva_cantidad)

        # ASSERT
        self.assertFalse(exito)
        self.assertIn("negativo", mensaje.lower())

    # ------------------------------------------------------------------
    # Prueba 7 – ajuste exitoso llama a UPDATE y a _registrar_alerta
    # ------------------------------------------------------------------
    @patch("models.inventario._registrar_alerta_si_necesario")
    @patch("models.inventario.db_cursor")
    def test_ajuste_exitoso_llama_alerta(self, mock_db, mock_alerta):
        # ARRANGE
        pid            = 7
        nueva_cantidad = 15
        cur = MagicMock()
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # ACT
        from models.inventario import ajustar_stock
        exito, mensaje = ajustar_stock(pid, nueva_cantidad)

        # ASSERT
        self.assertTrue(exito)
        mock_alerta.assert_called_once_with(pid)   # debe verificar alertas tras ajuste


class TestBuscarProductos(unittest.TestCase):
    """Pruebas para inventario.buscar_productos()"""

    # ------------------------------------------------------------------
    # Prueba 8 – búsqueda sin filtros retorna todos los productos activos
    # ------------------------------------------------------------------
    @patch("models.inventario.db_cursor")
    def test_busqueda_sin_filtros_retorna_lista(self, mock_db):
        # ARRANGE
        fila = _dict_row(
            id=1, codigo="FLT-001", nombre="Filtro aceite",
            descripcion="Estándar", categoria="Filtros", categoria_id=1,
            precio_unitario=15000.0, stock_actual=20,
            stock_minimo=5, activo=True
        )
        cur = MagicMock()
        cur.fetchall.return_value = [fila]
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # ACT
        from models.inventario import buscar_productos
        resultado = buscar_productos()

        # ASSERT
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].codigo, "FLT-001")

    # ------------------------------------------------------------------
    # Prueba 9 – búsqueda con texto filtra por nombre/código
    # ------------------------------------------------------------------
    @patch("models.inventario.db_cursor")
    def test_busqueda_con_texto_pasa_like_correcto(self, mock_db):
        # ARRANGE
        cur = MagicMock()
        cur.fetchall.return_value = []
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # ACT
        from models.inventario import buscar_productos
        buscar_productos(texto="filtro")

        # ASSERT – el execute debe recibir el patrón LIKE en minúsculas
        args = cur.execute.call_args[0]
        params = args[1]
        self.assertIn("%filtro%", params,
                      "El patrón LIKE debe estar en minúsculas y con %")


class TestDesactivarProducto(unittest.TestCase):
    """Pruebas para inventario.desactivar_producto()"""

    # ------------------------------------------------------------------
    # Prueba 10 – desactivar un producto ejecuta UPDATE correcto
    # ------------------------------------------------------------------
    @patch("models.inventario.db_cursor")
    def test_desactivar_producto_ejecuta_update(self, mock_db):
        # ARRANGE
        pid = 3
        cur = MagicMock()
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # ACT
        from models.inventario import desactivar_producto
        exito, mensaje = desactivar_producto(pid)

        # ASSERT
        self.assertTrue(exito)
        sql_usado = cur.execute.call_args[0][0]
        self.assertIn("activo=FALSE", sql_usado.replace(" ", "").upper().replace(
            "ACTIVO=FALSE", "activo=FALSE"))  # insensitive check
        self.assertIn(pid, cur.execute.call_args[0][1])


# ──────────────────────────────────────────────────────────────────────────────
# BLOQUE 2: models/auth.py
# ──────────────────────────────────────────────────────────────────────────────

class TestIniciarSesion(unittest.TestCase):
    """Pruebas para auth.iniciar_sesion()"""

    # ------------------------------------------------------------------
    # Prueba 11 – credenciales vacías deben retornar error sin consultar BD
    # ------------------------------------------------------------------
    def test_campos_vacios_retornan_error(self):
        # ARRANGE
        username = ""
        password = ""

        # ACT
        from models.auth import iniciar_sesion
        exito, mensaje, usuario = iniciar_sesion(username, password)

        # ASSERT
        self.assertFalse(exito)
        self.assertIsNone(usuario)
        self.assertIn("completa", mensaje.lower())

    # ------------------------------------------------------------------
    # Prueba 12 – username inexistente debe retornar mensaje genérico
    # ------------------------------------------------------------------
    @patch("models.auth.db_cursor")
    def test_usuario_inexistente_retorna_mensaje_generico(self, mock_db):
        # ARRANGE
        cur = MagicMock()
        cur.fetchone.return_value = None       # usuario no encontrado en BD
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # ACT
        from models.auth import iniciar_sesion
        exito, mensaje, usuario = iniciar_sesion("noexiste", "clave123")

        # ASSERT
        self.assertFalse(exito)
        self.assertIsNone(usuario)
        # El mensaje NO debe revelar si el usuario existe (seguridad)
        self.assertNotIn("usuario no encontrado", mensaje.lower())

    # ------------------------------------------------------------------
    # Prueba 13 – cuenta bloqueada debe impedirse el acceso
    # ------------------------------------------------------------------
    @patch("models.auth.db_cursor")
    def test_cuenta_bloqueada_retorna_error(self, mock_db):
        # ARRANGE
        fila_bloqueada = _dict_row(
            id=1, cedula="123", nombre="Juan", username="jgomez",
            password_hash="$2b$12$hash", activo=True, bloqueado=True,
            intentos_fallidos=3, rol="Vendedor"
        )
        cur = MagicMock()
        cur.fetchone.return_value = fila_bloqueada
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # ACT
        from models.auth import iniciar_sesion
        exito, mensaje, usuario = iniciar_sesion("jgomez", "cualquier_clave")

        # ASSERT
        self.assertFalse(exito)
        self.assertIsNone(usuario)
        self.assertIn("bloqueada", mensaje.lower())

    # ------------------------------------------------------------------
    # Prueba 14 – cuenta inactiva debe impedirse el acceso
    # ------------------------------------------------------------------
    @patch("models.auth.db_cursor")
    def test_cuenta_inactiva_retorna_error(self, mock_db):
        # ARRANGE
        fila_inactiva = _dict_row(
            id=2, cedula="456", nombre="Ana", username="aperez",
            password_hash="$2b$12$hash", activo=False, bloqueado=False,
            intentos_fallidos=0, rol="Inventario"
        )
        cur = MagicMock()
        cur.fetchone.return_value = fila_inactiva
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # ACT
        from models.auth import iniciar_sesion
        exito, mensaje, usuario = iniciar_sesion("aperez", "pass")

        # ASSERT
        self.assertFalse(exito)
        self.assertIsNone(usuario)
        self.assertIn("inactiva", mensaje.lower())

    # ------------------------------------------------------------------
    # Prueba 15 – login exitoso establece sesión y retorna el usuario
    # ------------------------------------------------------------------
    @patch("models.auth.bcrypt")
    @patch("models.auth.db_cursor")
    def test_login_exitoso_establece_sesion(self, mock_db, mock_bcrypt):
        # ARRANGE
        import bcrypt as bcrypt_real
        hash_real = bcrypt_real.hashpw(b"clave123", bcrypt_real.gensalt()).decode()

        fila_usuario = _dict_row(
            id=10, cedula="789", nombre="Carlos Mendez",
            username="cmendez", password_hash=hash_real,
            activo=True, bloqueado=False, intentos_fallidos=0,
            rol="Gerencia"
        )
        cur = MagicMock()
        cur.fetchone.return_value = fila_usuario
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # Simulamos que bcrypt verifica correctamente la contraseña
        mock_bcrypt.checkpw.return_value = True

        # ACT
        from models.auth import iniciar_sesion, get_usuario_activo
        exito, mensaje, usuario = iniciar_sesion("cmendez", "clave123")

        # ASSERT
        self.assertTrue(exito)
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.username, "cmendez")
        self.assertEqual(usuario.rol, "Gerencia")
        self.assertIn("bienvenido", mensaje.lower())


class TestHashPassword(unittest.TestCase):
    """Pruebas para auth.hash_password()"""

    # ------------------------------------------------------------------
    # Prueba 16 – el hash generado no es texto plano
    # ------------------------------------------------------------------
    def test_hash_no_contiene_password_plano(self):
        # ARRANGE
        password_plano = "MiContraseñaSegura123"

        # ACT
        from models.auth import hash_password
        resultado = hash_password(password_plano)

        # ASSERT
        self.assertNotEqual(resultado, password_plano,
                            "El hash no debe ser igual al texto plano")
        self.assertTrue(resultado.startswith("$2b$"),
                        "Debe ser un hash bcrypt válido (prefijo $2b$)")

    # ------------------------------------------------------------------
    # Prueba 17 – dos hashes del mismo password deben ser distintos (salt único)
    # ------------------------------------------------------------------
    def test_hashes_del_mismo_password_son_distintos(self):
        # ARRANGE
        password = "Segura123"

        # ACT
        from models.auth import hash_password
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # ASSERT
        self.assertNotEqual(hash1, hash2,
                            "Cada hash debe tener salt único (nunca iguales)")


class TestCerrarSesion(unittest.TestCase):
    """Pruebas para auth.cerrar_sesion()"""

    # ------------------------------------------------------------------
    # Prueba 18 – cerrar sesión limpia el usuario activo
    # ------------------------------------------------------------------
    def test_cerrar_sesion_limpia_usuario_activo(self):
        # ARRANGE – establecemos un usuario activo manualmente
        from models.auth import set_usuario_activo, get_usuario_activo, cerrar_sesion, Usuario
        usuario_fake = Usuario(
            id=1, cedula="000", nombre="Test", username="test",
            rol="Vendedor", activo=True, bloqueado=False
        )
        set_usuario_activo(usuario_fake)
        self.assertIsNotNone(get_usuario_activo())  # Pre-condición

        # ACT
        cerrar_sesion()

        # ASSERT
        self.assertIsNone(get_usuario_activo(),
                          "Después de cerrar sesión el usuario activo debe ser None")


class TestCrearUsuario(unittest.TestCase):
    """Pruebas para auth.crear_usuario()"""

    # ------------------------------------------------------------------
    # Prueba 19 – rol inexistente retorna error claro
    # ------------------------------------------------------------------
    @patch("models.auth.db_cursor")
    def test_rol_inexistente_retorna_error(self, mock_db):
        # ARRANGE
        cur = MagicMock()
        cur.fetchone.return_value = None   # rol no encontrado en BD
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # ACT
        from models.auth import crear_usuario
        exito, mensaje = crear_usuario(
            "111", "Nuevo User", "nuser", "pass123", "RolInexistente"
        )

        # ASSERT
        self.assertFalse(exito)
        self.assertIn("RolInexistente", mensaje)

    # ------------------------------------------------------------------
    # Prueba 20 – usuario duplicado retorna mensaje amigable
    # ------------------------------------------------------------------
    @patch("models.auth.hash_password", return_value="$2b$hash")
    @patch("models.auth.db_cursor")
    def test_usuario_duplicado_retorna_mensaje_claro(self, mock_db, _mock_hash):
        # ARRANGE
        cur = MagicMock()
        cur.fetchone.return_value = _dict_row(id=1)  # rol encontrado
        cur.execute.side_effect = [None, Exception("unique constraint violated")]
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # ACT
        from models.auth import crear_usuario
        exito, mensaje = crear_usuario(
            "222", "Duplicado", "dupuser", "pass", "Vendedor"
        )

        # ASSERT
        self.assertFalse(exito)
        self.assertIn("ya existe", mensaje.lower())


# ──────────────────────────────────────────────────────────────────────────────
# BLOQUE 3: models/ventas.py  (ItemVenta - lógica pura, sin BD)
# ──────────────────────────────────────────────────────────────────────────────

class TestItemVenta(unittest.TestCase):
    """Pruebas para la dataclass ventas.ItemVenta (cálculo de subtotal)"""

    # ------------------------------------------------------------------
    # Prueba 21 – el subtotal se calcula correctamente al crear el ítem
    # ------------------------------------------------------------------
    def test_subtotal_calculado_correctamente(self):
        # ARRANGE
        precio    = 15000.0
        cantidad  = 3
        esperado  = 45000.0

        # ACT
        from models.ventas import ItemVenta
        item = ItemVenta(
            producto_id=1, codigo="FLT-001", nombre="Filtro aceite",
            precio_unitario=precio, cantidad=cantidad
        )

        # ASSERT
        self.assertAlmostEqual(item.subtotal, esperado, places=2)

    # ------------------------------------------------------------------
    # Prueba 22 – subtotal con precio decimal se redondea a 2 decimales
    # ------------------------------------------------------------------
    def test_subtotal_redondeo_dos_decimales(self):
        # ARRANGE
        precio   = 10.333
        cantidad = 3
        # 10.333 * 3 = 30.999 → round(..., 2) = 31.0

        # ACT
        from models.ventas import ItemVenta
        item = ItemVenta(
            producto_id=2, codigo="TRN-001", nombre="Tornillo",
            precio_unitario=precio, cantidad=cantidad
        )

        # ASSERT
        self.assertEqual(item.subtotal, round(precio * cantidad, 2))

    # ------------------------------------------------------------------
    # Prueba 23 – cantidad de 1 unidad retorna el precio exacto
    # ------------------------------------------------------------------
    def test_subtotal_una_unidad_igual_al_precio(self):
        # ARRANGE
        precio   = 89900.0
        cantidad = 1

        # ACT
        from models.ventas import ItemVenta
        item = ItemVenta(
            producto_id=3, codigo="BUJ-001", nombre="Bujía NGK",
            precio_unitario=precio, cantidad=cantidad
        )

        # ASSERT
        self.assertEqual(item.subtotal, precio,
                         "Con cantidad=1, subtotal debe ser igual al precio unitario")


class TestBuscarClientes(unittest.TestCase):
    """Pruebas para ventas.buscar_clientes()"""

    # ------------------------------------------------------------------
    # Prueba 24 – la búsqueda usa LIKE en minúsculas con wildcards
    # ------------------------------------------------------------------
    @patch("models.ventas.db_cursor")
    def test_busqueda_usa_like_minusculas(self, mock_db):
        # ARRANGE
        cur = MagicMock()
        cur.fetchall.return_value = []
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # ACT
        from models.ventas import buscar_clientes
        buscar_clientes("GARCIA")

        # ASSERT
        params = cur.execute.call_args[0][1]
        self.assertIn("%garcia%", params,
                      "El patrón LIKE debe estar en minúsculas")

    # ------------------------------------------------------------------
    # Prueba 25 – resultado vacío retorna lista vacía (no lanza excepción)
    # ------------------------------------------------------------------
    @patch("models.ventas.db_cursor")
    def test_sin_resultados_retorna_lista_vacia(self, mock_db):
        # ARRANGE
        cur = MagicMock()
        cur.fetchall.return_value = []
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # ACT
        from models.ventas import buscar_clientes
        resultado = buscar_clientes("XYZ_NO_EXISTE")

        # ASSERT
        self.assertIsInstance(resultado, list)
        self.assertEqual(len(resultado), 0)


# ──────────────────────────────────────────────────────────────────────────────
# BLOQUE 4: Casos de borde y robustez
# ──────────────────────────────────────────────────────────────────────────────

class TestRobustezInventario(unittest.TestCase):
    """Pruebas de robustez: entradas límite y manejo de errores inesperados"""

    # ------------------------------------------------------------------
    # Prueba 26 – precio de 0 es válido (producto gratuito/muestra)
    # ------------------------------------------------------------------
    @patch("models.inventario.db_cursor")
    def test_precio_cero_es_valido(self, mock_db):
        # ARRANGE
        cur = MagicMock()
        cur.fetchone.return_value = _dict_row(id=99)
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # ACT
        from models.inventario import registrar_producto
        exito, _ = registrar_producto("MUESTRA-01", "Muestra", "", 1, 0.0, 1, 0)

        # ASSERT
        self.assertTrue(exito, "Precio 0 debe ser permitido (muestra/regalo)")

    # ------------------------------------------------------------------
    # Prueba 27 – error de BD inesperado en registrar_producto retorna False
    # ------------------------------------------------------------------
    @patch("models.inventario.db_cursor")
    def test_error_bd_retorna_false_con_mensaje(self, mock_db):
        # ARRANGE
        cur = MagicMock()
        cur.execute.side_effect = Exception("connection timeout")
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # ACT
        from models.inventario import registrar_producto
        exito, mensaje = registrar_producto(
            "ERR-001", "Producto BD caída", "", 1, 5000.0, 5, 1
        )

        # ASSERT
        self.assertFalse(exito)
        self.assertIn("error", mensaje.lower(),
                      "El mensaje debe indicar que hubo un error")

    # ------------------------------------------------------------------
    # Prueba 28 – obtener_producto inexistente retorna None (no lanza excepción)
    # ------------------------------------------------------------------
    @patch("models.inventario.db_cursor")
    def test_obtener_producto_inexistente_retorna_none(self, mock_db):
        # ARRANGE
        cur = MagicMock()
        cur.fetchone.return_value = None   # producto no existe en BD
        mock_db.return_value.__enter__.return_value = cur
        mock_db.return_value.__exit__.return_value = False

        # ACT
        from models.inventario import obtener_producto
        resultado = obtener_producto(pid=9999)

        # ASSERT
        self.assertIsNone(resultado,
                          "Producto inexistente debe retornar None, no lanzar excepción")


# ──────────────────────────────────────────────────────────────────────────────
# Punto de entrada para ejecución directa
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    unittest.main(verbosity=2)
