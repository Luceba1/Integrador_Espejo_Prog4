from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response, status

from app.core.auth_dependencies import get_current_user
from app.models.usuario import Usuario
from app.schemas.direccion_schema import DireccionCreate, DireccionRead, DireccionUpdate
from app.services import direccion_service
from app.uow.unit_of_work import SQLModelUnitOfWork, get_uow

router = APIRouter(prefix="/direcciones", tags=["Direcciones de entrega"])

UowDep = Annotated[SQLModelUnitOfWork, Depends(get_uow)]
CurrentUserDep = Annotated[Usuario, Depends(get_current_user)]


@router.get("/", response_model=list[DireccionRead], status_code=status.HTTP_200_OK)
def listar_direcciones(uow: UowDep, usuario: CurrentUserDep) -> list[DireccionRead]:
    return direccion_service.listar(uow, usuario)


@router.get("/{direccion_id}", response_model=DireccionRead, status_code=status.HTTP_200_OK)
def obtener_direccion(
    uow: UowDep,
    usuario: CurrentUserDep,
    direccion_id: int = Path(..., ge=1),
) -> DireccionRead:
    return direccion_service.obtener_por_id(uow, usuario, direccion_id)


@router.post("/", response_model=DireccionRead, status_code=status.HTTP_201_CREATED)
def crear_direccion(
    payload: DireccionCreate,
    uow: UowDep,
    usuario: CurrentUserDep,
) -> DireccionRead:
    return direccion_service.crear(uow, usuario, payload)


@router.put("/{direccion_id}", response_model=DireccionRead, status_code=status.HTTP_200_OK)
def actualizar_direccion(
    payload: DireccionUpdate,
    uow: UowDep,
    usuario: CurrentUserDep,
    direccion_id: int = Path(..., ge=1),
) -> DireccionRead:
    return direccion_service.actualizar(uow, usuario, direccion_id, payload)


@router.patch(
    "/{direccion_id}/principal",
    response_model=DireccionRead,
    status_code=status.HTTP_200_OK,
)
def marcar_direccion_principal(
    uow: UowDep,
    usuario: CurrentUserDep,
    direccion_id: int = Path(..., ge=1),
) -> DireccionRead:
    return direccion_service.marcar_principal(uow, usuario, direccion_id)


@router.delete("/{direccion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_direccion(
    uow: UowDep,
    usuario: CurrentUserDep,
    direccion_id: int = Path(..., ge=1),
) -> Response:
    direccion_service.eliminar(uow, usuario, direccion_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
