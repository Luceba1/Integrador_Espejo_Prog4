from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.core.auth_dependencies import UowDep, require_roles
from app.models.usuario import Usuario
from app.schemas.unidad_medida_schema import UnidadMedidaCreate, UnidadMedidaRead, UnidadMedidaUpdate
from app.services import unidad_medida_service

router = APIRouter(prefix="/unidades-medida", tags=["Unidades de medida"])
AdminDep = Annotated[Usuario, Depends(require_roles("ADMIN"))]
AdminStockDep = Annotated[Usuario, Depends(require_roles("ADMIN", "STOCK"))]


@router.get("/", response_model=list[UnidadMedidaRead])
def listar_unidades_medida(
    uow: UowDep,
    _usuario: AdminStockDep,
    incluir_eliminadas: Annotated[bool, Query()] = False,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[UnidadMedidaRead]:
    return unidad_medida_service.listar(uow, incluir_eliminadas=incluir_eliminadas, page=page, size=size)


@router.get("/{unidad_id}", response_model=UnidadMedidaRead)
def obtener_unidad_medida(
    unidad_id: Annotated[int, Path(ge=1)],
    uow: UowDep,
    _usuario: AdminStockDep,
) -> UnidadMedidaRead:
    return unidad_medida_service.obtener(uow, unidad_id)


@router.post("/", response_model=UnidadMedidaRead, status_code=status.HTTP_201_CREATED)
def crear_unidad_medida(
    payload: UnidadMedidaCreate,
    uow: UowDep,
    _admin: AdminDep,
) -> UnidadMedidaRead:
    return unidad_medida_service.crear(uow, payload)


@router.put("/{unidad_id}", response_model=UnidadMedidaRead)
def actualizar_unidad_medida(
    unidad_id: Annotated[int, Path(ge=1)],
    payload: UnidadMedidaUpdate,
    uow: UowDep,
    _admin: AdminDep,
) -> UnidadMedidaRead:
    return unidad_medida_service.actualizar(uow, unidad_id, payload)


@router.patch("/{unidad_id}/activar", response_model=UnidadMedidaRead)
def activar_unidad_medida(
    unidad_id: Annotated[int, Path(ge=1)],
    uow: UowDep,
    _admin: AdminDep,
) -> UnidadMedidaRead:
    return unidad_medida_service.activar(uow, unidad_id)


@router.delete("/{unidad_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_unidad_medida(
    unidad_id: Annotated[int, Path(ge=1)],
    uow: UowDep,
    _admin: AdminDep,
) -> Response:
    unidad_medida_service.eliminar(uow, unidad_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
