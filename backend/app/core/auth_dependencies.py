from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, Header, HTTPException, status

from app.core.security import decode_access_token
from app.models.usuario import Usuario
from app.services.auth_service import obtener_usuario_actual, roles_codigos
from app.uow.unit_of_work import SQLModelUnitOfWork, get_uow

UowDep = Annotated[SQLModelUnitOfWork, Depends(get_uow)]


def _extraer_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token.strip()


def get_current_user(
    uow: UowDep,
    access_token: Annotated[str | None, Cookie(alias="access_token")] = None,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> Usuario:
    token = access_token or _extraer_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No hay sesión activa.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(token)
        usuario_id = int(payload.get("sub"))
    except (jwt.InvalidTokenError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o vencido.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return obtener_usuario_actual(uow, usuario_id)


def require_roles(*roles_permitidos: str) -> Callable[[Usuario], Usuario]:
    def dependency(usuario: Annotated[Usuario, Depends(get_current_user)]) -> Usuario:
        roles_usuario = set(roles_codigos(usuario))
        if not roles_usuario.intersection(roles_permitidos):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tenés permisos para realizar esta acción.",
            )
        return usuario

    return dependency
