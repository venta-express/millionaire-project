"""
AutoParts Express - Modelo de Auditoria
Sprint 4: Registro de acciones del sistema para trazabilidad completa.
"""

import json
from datetime import datetime
from typing import Optional
from db.connection import db_cursor


def registrar_accion(
    usuario_id: int,
    accion: str,
    modulo: str,
    detalle: Optional[dict] = None,
    ip: str = "127.0.0.1"
) -> None:
    """Registra una accion en el log de auditoria."""
    detalle_str = json.dumps(detalle, default=str) if detalle else None
    with db_cursor(commit=True) as cur:
        cur.execute("""
            INSERT INTO auditoria (usuario_id, accion, modulo, detalle, ip)
            VALUES (%s, %s, %s, %s, %s)
        """, (usuario_id, accion, modulo, detalle_str, ip))


def obtener_auditoria(
    modulo: Optional[str] = None,
    usuario_id: Optional[int] = None,
    limit: int = 200
) -> list:
    """Obtiene el log de auditoria con filtros opcionales."""
    condiciones = []
    params = []

    if modulo:
        condiciones.append("a.modulo = %s")
        params.append(modulo)
    if usuario_id:
        condiciones.append("a.usuario_id = %s")
        params.append(usuario_id)

    where = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""
    params.append(limit)

    with db_cursor() as cur:
        cur.execute(f"""
            SELECT a.id, u.nombre AS usuario, u.username, a.accion,
                   a.modulo, a.detalle, a.fecha_hora, a.ip
            FROM auditoria a
            LEFT JOIN usuarios u ON u.id = a.usuario_id
            {where}
            ORDER BY a.fecha_hora DESC
            LIMIT %s
        """, params)
        return [dict(r) for r in cur.fetchall()]
