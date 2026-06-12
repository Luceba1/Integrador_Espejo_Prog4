"""Utilidades de autenticación/autorización para WebSocket."""

from __future__ import annotations

from dataclasses import dataclass

import jwt
from fastapi import HTTPException, WebSocket, status

from app.core.security import decode_access_token
from app.models.pedido import Pedido
from app.services.auth_service import roles_codigos
from app.uow.unit_of_work import SQLModelUnitOfWork

ROLES_GESTION_PEDIDOS = {"ADMIN", "PEDIDOS"}


@dataclass(frozen=True)
class UsuarioWS:
    """Datos mínimos del usuario autenticado para WebSocket.

    No devolvemos el modelo SQLModel/SQLAlchemy porque al cerrar el UnitOfWork
    la instancia queda desacoplada de la sesión y puede provocar
    DetachedInstanceError al acceder a atributos como id o roles.
    """

    id: int
    roles: set[str]


def extraer_token_ws(websocket: WebSocket, token_query: str | None) -> str | None:
    """Obtiene JWT desde cookie HttpOnly o query ?token=... para pruebas."""

    token = websocket.cookies.get("access_token") or token_query
    if not token:
        return None
    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1]
    return token.strip()


def validar_usuario_ws(token: str, roles_permitidos: set[str] | None = None) -> UsuarioWS:
    try:
        payload = decode_access_token(token)
        usuario_id = int(payload.get("sub"))
    except (jwt.InvalidTokenError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o vencido.") from exc

    with SQLModelUnitOfWork() as uow:
        usuario = uow.usuarios.get_active_by_id(usuario_id)
        if usuario is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inválido o inactivo.")

        roles_usuario = set(roles_codigos(usuario))
        if roles_permitidos is not None and not roles_usuario.intersection(roles_permitidos):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes.")

        # Devolvemos datos simples, seguros para usar fuera de la sesión.
        return UsuarioWS(id=usuario.id, roles=roles_usuario)


def validar_acceso_pedido_ws(usuario: UsuarioWS, pedido: Pedido | None) -> None:
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado.")

    if usuario.roles.intersection(ROLES_GESTION_PEDIDOS):
        return

    if pedido.usuario_id != usuario.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No podés seguir un pedido de otro usuario.")
