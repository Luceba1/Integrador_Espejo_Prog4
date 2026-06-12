from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.core.auth_dependencies import require_roles
from app.models.usuario import Usuario
from app.schemas.ingrediente_schema import (
    IngredienteCreate,
    IngredienteRead,
    IngredienteUpdate,
)
from app.services import ingrediente_service
from app.uow.unit_of_work import SQLModelUnitOfWork, get_uow

router = APIRouter(prefix="/ingredientes", tags=["Ingredientes"])

UowDep = Annotated[SQLModelUnitOfWork, Depends(get_uow)]
AdminDep = Annotated[Usuario, Depends(require_roles("ADMIN"))]


@router.get("/", response_model=list[IngredienteRead], status_code=status.HTTP_200_OK)
def listar_ingredientes(
    uow: UowDep,
    incluir_eliminados: Annotated[bool, Query()] = False,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[IngredienteRead]:
    return ingrediente_service.listar(uow, incluir_eliminados=incluir_eliminados, page=page, size=size)


@router.get("/{ingrediente_id}", response_model=IngredienteRead, status_code=status.HTTP_200_OK)
def obtener_ingrediente(
    uow: UowDep,
    ingrediente_id: int = Path(..., ge=1),
) -> IngredienteRead:
    return ingrediente_service.obtener_por_id(uow, ingrediente_id)


@router.post("/", response_model=IngredienteRead, status_code=status.HTTP_201_CREATED)
def crear_ingrediente(payload: IngredienteCreate, uow: UowDep, _admin: AdminDep) -> IngredienteRead:
    return ingrediente_service.crear(uow, payload)


@router.put("/{ingrediente_id}", response_model=IngredienteRead, status_code=status.HTTP_200_OK)
def actualizar_ingrediente(
    payload: IngredienteUpdate,
    uow: UowDep,
    _admin: AdminDep,
    ingrediente_id: int = Path(..., ge=1),
) -> IngredienteRead:
    return ingrediente_service.actualizar(uow, ingrediente_id, payload)


@router.patch("/{ingrediente_id}/activar", response_model=IngredienteRead, status_code=status.HTTP_200_OK)
def activar_ingrediente(
    uow: UowDep,
    _admin: AdminDep,
    ingrediente_id: int = Path(..., ge=1),
) -> IngredienteRead:
    return ingrediente_service.activar(uow, ingrediente_id)


@router.delete("/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ingrediente(
    uow: UowDep,
    _admin: AdminDep,
    ingrediente_id: int = Path(..., ge=1),
) -> Response:
    ingrediente_service.eliminar(uow, ingrediente_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
