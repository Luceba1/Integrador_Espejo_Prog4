from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.auth_dependencies import UowDep, require_roles
from app.models.usuario import Usuario
from app.schemas.admin_schema import UsuarioAdminRead, UsuarioAdminUpdate, UsuarioRolesUpdate
from app.schemas.auth_schema import RolRead
from app.services.admin_service import (
    actualizar_usuario,
    activar_usuario,
    asignar_roles,
    eliminar_usuario,
    listar_usuarios,
    obtener_usuario_admin,
)

router = APIRouter(prefix="/admin", tags=["Administración"])
AdminUserDep = Annotated[Usuario, Depends(require_roles("ADMIN"))]


@router.get("/roles", response_model=list[RolRead])
def listar_roles_admin(
    uow: UowDep,
    _: AdminUserDep,
):
    return uow.roles.list_active()


@router.get("/usuarios", response_model=list[UsuarioAdminRead])
def listar_usuarios_admin(
    uow: UowDep,
    _: AdminUserDep,
    rol: Annotated[str | None, Query(description="Filtrar por código de rol: ADMIN, STOCK, PEDIDOS o CLIENT")] = None,
    search: Annotated[str | None, Query(description="Buscar por email, nombre o apellido")] = None,
    incluir_eliminados: bool = False,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 10,
) -> list[Usuario]:
    return listar_usuarios(
        uow,
        rol=rol,
        search=search,
        incluir_eliminados=incluir_eliminados,
        page=page,
        size=size,
    )


@router.get("/usuarios/{usuario_id}", response_model=UsuarioAdminRead)
def obtener_usuario_admin_endpoint(
    usuario_id: int,
    uow: UowDep,
    _: AdminUserDep,
) -> Usuario:
    return obtener_usuario_admin(uow, usuario_id)


@router.put("/usuarios/{usuario_id}", response_model=UsuarioAdminRead)
def actualizar_usuario_admin_endpoint(
    usuario_id: int,
    payload: UsuarioAdminUpdate,
    uow: UowDep,
    _: AdminUserDep,
) -> Usuario:
    return actualizar_usuario(uow, usuario_id, payload)


@router.patch("/usuarios/{usuario_id}/roles", response_model=UsuarioAdminRead)
def asignar_roles_usuario_endpoint(
    usuario_id: int,
    payload: UsuarioRolesUpdate,
    uow: UowDep,
    usuario_actual: AdminUserDep,
) -> Usuario:
    return asignar_roles(uow, usuario_id, payload, usuario_actual)


@router.patch("/usuarios/{usuario_id}/activar", response_model=UsuarioAdminRead, status_code=status.HTTP_200_OK)
def activar_usuario_admin_endpoint(
    usuario_id: int,
    uow: UowDep,
    _: AdminUserDep,
) -> Usuario:
    return activar_usuario(uow, usuario_id)


@router.delete("/usuarios/{usuario_id}", response_model=UsuarioAdminRead, status_code=status.HTTP_200_OK)
def eliminar_usuario_admin_endpoint(
    usuario_id: int,
    uow: UowDep,
    usuario_actual: AdminUserDep,
) -> Usuario:
    return eliminar_usuario(uow, usuario_id, usuario_actual)
