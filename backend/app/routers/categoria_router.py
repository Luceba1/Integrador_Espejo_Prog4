from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.core.auth_dependencies import require_roles
from app.models.usuario import Usuario
from app.schemas.categoria_schema import (
    CategoriaCreate,
    CategoriaRead,
    CategoriaTreeRead,
    CategoriaUpdate,
)
from app.services import categoria_service
from app.uow.unit_of_work import SQLModelUnitOfWork, get_uow

router = APIRouter(prefix="/categorias", tags=["Categorías"])

UowDep = Annotated[SQLModelUnitOfWork, Depends(get_uow)]
AdminDep = Annotated[Usuario, Depends(require_roles("ADMIN"))]


@router.get("/", response_model=list[CategoriaRead], status_code=status.HTTP_200_OK)
def listar_categorias(
    uow: UowDep,
    parent_id: Annotated[int | None, Query(ge=1)] = None,
    solo_raiz: Annotated[bool, Query(description="Si es true, devuelve solo categorías raíz.")] = False,
    incluir_eliminadas: Annotated[bool, Query()] = False,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[CategoriaRead]:
    return categoria_service.listar(
        uow,
        parent_id=parent_id,
        solo_raiz=solo_raiz,
        incluir_eliminadas=incluir_eliminadas,
        page=page,
        size=size,
    )


@router.get("/arbol", response_model=list[CategoriaTreeRead], status_code=status.HTTP_200_OK)
def listar_categorias_arbol(
    uow: UowDep,
    incluir_eliminadas: Annotated[bool, Query()] = False,
) -> list[CategoriaTreeRead]:
    return categoria_service.listar_arbol(uow, incluir_eliminadas=incluir_eliminadas)


@router.get("/{categoria_id}", response_model=CategoriaRead, status_code=status.HTTP_200_OK)
def obtener_categoria(
    uow: UowDep,
    categoria_id: int = Path(..., ge=1),
) -> CategoriaRead:
    return categoria_service.obtener_por_id(uow, categoria_id)


@router.post("/", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
def crear_categoria(payload: CategoriaCreate, uow: UowDep, _admin: AdminDep) -> CategoriaRead:
    return categoria_service.crear(uow, payload)


@router.put("/{categoria_id}", response_model=CategoriaRead, status_code=status.HTTP_200_OK)
def actualizar_categoria(
    payload: CategoriaUpdate,
    uow: UowDep,
    _admin: AdminDep,
    categoria_id: int = Path(..., ge=1),
) -> CategoriaRead:
    return categoria_service.actualizar(uow, categoria_id, payload)


@router.patch("/{categoria_id}/activar", response_model=CategoriaRead, status_code=status.HTTP_200_OK)
def activar_categoria(
    uow: UowDep,
    _admin: AdminDep,
    categoria_id: int = Path(..., ge=1),
) -> CategoriaRead:
    return categoria_service.activar(uow, categoria_id)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(
    uow: UowDep,
    _admin: AdminDep,
    categoria_id: int = Path(..., ge=1),
) -> Response:
    categoria_service.eliminar(uow, categoria_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
