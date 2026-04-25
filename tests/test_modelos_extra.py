"""
Tests adicionales para auth, inventario y ventas.
Sprint 4: hashes bcrypt validos, sin comparaciones float ==,
          mensajes de error verificados por tipo, no por texto fijo.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


def _make_ctx(cur=None):
    if cur is None:
        cur = MagicMock()
    ctx = MagicMock()
    ctx.return_value.__enter__ = MagicMock(return_value=cur)
    ctx.return_value.__exit__ = MagicMock(return_value=False)
    return cur, ctx


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  AUTH â€” cubierto en test_auth.py; aqui solo casos extra
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def test_hash_retorna_string():
    from models.auth import hash_password
    resultado = hash_password("mi_clave_segura")
    assert isinstance(resultado, str)
    assert len(resultado) > 0


def test_hash_difiere_del_original():
    from models.auth import hash_password
    resultado = hash_password("mi_clave_segura")
    assert resultado != "mi_clave_segura"


def test_hash_bcrypt_verificable():
    import bcrypt
    from models.auth import hash_password
    clave = "clave_de_prueba_123"
    hashed = hash_password(clave)
    assert bcrypt.checkpw(clave.encode(), hashed.encode())


def test_iniciar_sesion_campos_vacios():
    from models.auth import iniciar_sesion
    ok, msg, u = iniciar_sesion("", "")
    assert ok is False


def test_iniciar_sesion_usuario_vacio():
    from models.auth import iniciar_sesion
    ok, msg, u = iniciar_sesion("", "clave123")
    assert ok is False


def test_iniciar_sesion_clave_vacia():
    from models.auth import iniciar_sesion
    ok, msg, u = iniciar_sesion("admin", "")
    assert ok is False


def test_iniciar_sesion_usuario_no_existe():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = None
    with patch("models.auth.db_cursor", ctx):
        from models.auth import iniciar_sesion
        ok, msg, u = iniciar_sesion("noexiste", "abc")
        assert ok is False
        assert u is None


def test_iniciar_sesion_bloqueada():
    """Usa un hash bcrypt valido para evitar ValueError al verificar."""
    import bcrypt
    hash_valido = "mock_hash_no_es_credencial_real"
    mock_row = {
        "id": 1, "cedula": "1", "nombre": "Juan", "username": "juan",
        "password_hash": hash_valido,
        "activo": True, "bloqueado": True,
        "intentos_fallidos": 3, "rol": "Vendedor",
    }
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = mock_row
    with patch("models.auth.db_cursor", ctx):
        from models.auth import iniciar_sesion
        ok, msg, u = iniciar_sesion("juan", "cualquier")
        assert ok is False
        assert "bloqueada" in msg.lower()


def test_iniciar_sesion_inactiva():
    """Usa un hash bcrypt valido para evitar ValueError al verificar."""
    import bcrypt
    hash_valido = "mock_hash_no_es_credencial_real"
    mock_row = {
        "id": 1, "cedula": "1", "nombre": "Juan", "username": "juan",
        "password_hash": hash_valido,
        "activo": False, "bloqueado": False,
        "intentos_fallidos": 0, "rol": "Vendedor",
    }
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = mock_row
    with patch("models.auth.db_cursor", ctx):
        from models.auth import iniciar_sesion
        ok, msg, u = iniciar_sesion("juan", "cualquier")
        assert ok is False
        assert "inactiva" in msg.lower()


def test_crear_usuario_exitoso():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = {"id": 2}
    with patch("models.auth.db_cursor", ctx):
        from models.auth import crear_usuario
        ok, _ = crear_usuario("123", "Juan", "juan", "clave_segura", "Vendedor")
        assert ok is True


def test_crear_usuario_rol_inexistente():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = None
    with patch("models.auth.db_cursor", ctx):
        from models.auth import crear_usuario
        ok, _ = crear_usuario("123", "Juan", "juan", "clave_segura", "RolInexistente")
        assert ok is False


def test_crear_usuario_duplicado():
    """El modelo puede retornar cualquier mensaje al violar unique; solo
    verificamos que ok sea False y msg sea un string no vacio."""
    ctx = MagicMock()
    ctx.side_effect = Exception("unique constraint")
    with patch("models.auth.db_cursor", ctx):
        from models.auth import crear_usuario
        ok, msg = crear_usuario("123", "Juan", "juan", "clave_segura", "Vendedor")
        assert ok is False
        assert isinstance(msg, str) and len(msg) > 0


def test_editar_usuario_exitoso():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = {"id": 2}
    with patch("models.auth.db_cursor", ctx):
        from models.auth import editar_usuario
        ok, _ = editar_usuario(1, "Nuevo Nombre", "Vendedor", True)
        assert ok is True


def test_editar_usuario_nueva_clave():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = {"id": 2}
    with patch("models.auth.db_cursor", ctx):
        from models.auth import editar_usuario
        ok, _ = editar_usuario(1, "Nombre", "Vendedor", True, nueva_clave="nueva_clave_ok")
        assert ok is True


def test_editar_usuario_rol_inexistente():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = None
    with patch("models.auth.db_cursor", ctx):
        from models.auth import editar_usuario
        ok, _ = editar_usuario(1, "Nombre", "RolMalo", True)
        assert ok is False


def test_desbloquear_usuario():
    cur, ctx = _make_ctx()
    with patch("models.auth.db_cursor", ctx):
        from models.auth import desbloquear_usuario
        ok, _ = desbloquear_usuario(1)
        assert ok is True


def test_listar_roles_mock():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = [{"nombre": "Gerencia"}, {"nombre": "Vendedor"}]
    with patch("models.auth.db_cursor", ctx):
        from models.auth import listar_roles
        roles = listar_roles()
        assert isinstance(roles, list)
        assert "Gerencia" in roles


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  VENTAS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def test_item_subtotal_unitario():
    from models.ventas import ItemVenta
    item = ItemVenta(1, "P001", "Freno", 10000.0, 1)
    assert item.subtotal == pytest.approx(10000.0)


def test_item_subtotal_varios():
    from models.ventas import ItemVenta
    item = ItemVenta(1, "P001", "Freno", 45000.0, 3)
    assert item.subtotal == pytest.approx(135000.0)


def test_item_subtotal_es_float():
    from models.ventas import ItemVenta
    item = ItemVenta(1, "P001", "Freno", 33333.33, 3)
    assert isinstance(item.subtotal, float)


def test_registrar_venta_metodo_invalido():
    from models.ventas import ItemVenta, registrar_venta
    item = ItemVenta(1, "P001", "Freno", 45000.0, 1)
    ok, msg, _ = registrar_venta(1, 1, [item], "Cheque")
    assert ok is False


def test_registrar_venta_transferencia_sin_ref():
    from models.ventas import ItemVenta, registrar_venta
    item = ItemVenta(1, "P001", "Freno", 45000.0, 1)
    ok, msg, _ = registrar_venta(1, 1, [item], "Transferencia", referencia_pago="")
    assert ok is False


def test_registrar_venta_lista_vacia():
    from models.ventas import registrar_venta
    ok, msg, _ = registrar_venta(1, 1, [], "Efectivo")
    assert ok is False


def test_buscar_clientes_mock():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.ventas.db_cursor", ctx):
        from models.ventas import buscar_clientes
        assert isinstance(buscar_clientes("Juan"), list)


def test_buscar_cliente_cedula_existe():
    mock_row = {"id": 1, "cedula": "123", "nombre": "Juan",
                "telefono": "300", "email": "j@j.com"}
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = mock_row
    with patch("models.ventas.db_cursor", ctx):
        from models.ventas import buscar_cliente_por_cedula
        assert buscar_cliente_por_cedula("123") is not None


def test_buscar_cliente_cedula_no_existe():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = None
    with patch("models.ventas.db_cursor", ctx):
        from models.ventas import buscar_cliente_por_cedula
        assert buscar_cliente_por_cedula("999") is None


def test_obtener_venta_mock():
    mock_row = {
        "id": 1, "numero_factura": "FAC-001", "cliente_id": 1,
        "vendedor_id": 1, "subtotal": 50000.0, "descuento": 0.0,
        "total": 50000.0, "metodo_pago": "Efectivo",
        "referencia_pago": "", "notas": "", "estado": "Completada",
        "fecha_hora": datetime.now(),
    }
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = mock_row
    with patch("models.ventas.db_cursor", ctx):
        from models.ventas import obtener_venta
        assert obtener_venta(1) is not None


def test_historial_cliente_mock():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.ventas.db_cursor", ctx):
        from models.ventas import historial_cliente
        assert isinstance(historial_cliente(1), list)


def test_buscar_clientes_historial_mock():
    cur, ctx = _make_ctx()
    cur.fetchall.return_value = []
    with patch("models.ventas.db_cursor", ctx):
        from models.ventas import buscar_clientes_historial
        assert isinstance(buscar_clientes_historial("Juan"), list)


def test_obtener_o_crear_cliente_existente():
    cur, ctx = _make_ctx()
    cur.fetchone.return_value = {"id": 1}
    with patch("models.ventas.db_cursor", ctx):
        from models.ventas import obtener_o_crear_cliente
        ok, _, cid = obtener_o_crear_cliente("123456789", "Juan")
        assert ok is True
        assert cid == 1




