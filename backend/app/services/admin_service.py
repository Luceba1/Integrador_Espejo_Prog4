from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.models.usuario import Usuario
from app.schemas.admin_schema import UsuarioAdminUpdate, UsuarioRolesUpdate
from app.uow.unit_of_work import SQLModelUnitOfWork


ROLES_VALIDOS = {"ADMIN", "STOCK", "PEDIDOS", "CLIENT"}


def listar_usuarios(
    uow: SQLModelUnitOfWork,
    rol: str | None = None,
    search: str | None = None,
    incluir_eliminados: bool = False,
    page: int = 1,
    size: int = 10,
) -> list[Usuario]:
    if rol and rol.upper().strip() not in ROLES_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol inválido. Usá ADMIN, STOCK, PEDIDOS o CLIENT.",
        )

    return uow.usuarios.list_paginated_admin(
        rol_codigo=rol.upper().strip() if rol else None,
        search=search,
        incluir_eliminados=incluir_eliminados,
        page=page,
        size=size,
    )


def obtener_usuario_admin(uow: SQLModelUnitOfWork, usuario_id: int) -> Usuario:
    usuario = uow.usuarios.get_by_id_with_roles(usuario_id)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )
    return usuario


def actualizar_usuario(
    uow: SQLModelUnitOfWork,
    usuario_id: int,
    payload: UsuarioAdminUpdate,
) -> Usuario:
    usuario = obtener_usuario_admin(uow, usuario_id)

    if usuario.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede actualizar un usuario eliminado.",
        )

    if payload.email is not None:
        email = str(payload.email).lower().strip()
        existente = uow.usuarios.get_by_email_any_status(email)
        if existente is not None and existente.id != usuario.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe otro usuario con ese email.",
            )
        usuario.email = email

    if payload.nombre is not None:
        usuario.nombre = payload.nombre.strip()

    if payload.apellido is not None:
        usuario.apellido = payload.apellido.strip() or None

    if payload.activo is not None:
        usuario.activo = payload.activo
        if payload.activo:
            usuario.deleted_at = None

    usuario.updated_at = datetime.now(timezone.utc)
    return uow.usuarios.update(usuario)


def eliminar_usuario(uow: SQLModelUnitOfWork, usuario_id: int, usuario_actual: Usuario) -> Usuario:
    if usuario_actual.id == usuario_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No podés eliminar tu propio usuario administrador.",
        )

    usuario = obtener_usuario_admin(uow, usuario_id)
    if usuario.deleted_at is not None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado o ya eliminado.",
        )

    usuario.activo = False
    usuario.deleted_at = datetime.now(timezone.utc)
    usuario.updated_at = datetime.now(timezone.utc)
    return uow.usuarios.update(usuario)


def asignar_roles(
    uow: SQLModelUnitOfWork,
    usuario_id: int,
    payload: UsuarioRolesUpdate,
    usuario_actual: Usuario,
) -> Usuario:
    usuario = obtener_usuario_admin(uow, usuario_id)

    if usuario.deleted_at is not None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pueden asignar roles a un usuario eliminado o inactivo.",
        )

    roles_normalizados = sorted({codigo.upper().strip() for codigo in payload.roles})
    if not roles_normalizados:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario debe tener al menos un rol.",
        )

    invalidos = [codigo for codigo in roles_normalizados if codigo not in ROLES_VALIDOS]
    if invalidos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Roles inválidos: {', '.join(invalidos)}.",
        )

    if usuario_actual.id == usuario_id and "ADMIN" not in roles_normalizados:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No podés quitarte el rol ADMIN a vos mismo.",
        )

    roles = []
    for codigo in roles_normalizados:
        rol = uow.roles.get_by_codigo(codigo)
        if rol is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"No existe el rol {codigo}. Ejecutá el seed obligatorio.",
            )
        roles.append(rol)

    usuario.roles = roles
    usuario.updated_at = datetime.now(timezone.utc)
    return uow.usuarios.update(usuario)


def activar_usuario(uow: SQLModelUnitOfWork, usuario_id: int) -> Usuario:
    usuario = obtener_usuario_admin(uow, usuario_id)
    usuario.activo = True
    usuario.deleted_at = None
    usuario.updated_at = datetime.now(timezone.utc)
    return uow.usuarios.update(usuario)
