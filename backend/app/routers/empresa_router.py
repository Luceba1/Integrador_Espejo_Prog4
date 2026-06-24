from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.auth_dependencies import UowDep, require_roles
from app.models.usuario import Usuario
from app.schemas.empresa_schema import ConfiguracionEmpresaRead, ConfiguracionEmpresaUpdate
from app.services.empresa_service import actualizar_configuracion_empresa, obtener_configuracion_empresa

router = APIRouter(prefix="/empresa", tags=["Empresa"])
AdminUserDep = Annotated[Usuario, Depends(require_roles("ADMIN"))]


@router.get("/configuracion", response_model=ConfiguracionEmpresaRead)
def obtener_configuracion_empresa_publica(uow: UowDep) -> ConfiguracionEmpresaRead:
    return obtener_configuracion_empresa(uow)


@router.put("/configuracion", response_model=ConfiguracionEmpresaRead)
def actualizar_configuracion_empresa_admin(
    payload: ConfiguracionEmpresaUpdate,
    uow: UowDep,
    _: AdminUserDep,
) -> ConfiguracionEmpresaRead:
    return actualizar_configuracion_empresa(uow, payload)
