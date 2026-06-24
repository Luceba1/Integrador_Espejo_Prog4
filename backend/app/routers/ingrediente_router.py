from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Path, Query, Response, status

from app.core.auth_dependencies import require_roles
from app.core.websocket import manager
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


def _avisar_catalogo(background_tasks: BackgroundTasks, event: str, **data: object) -> None:
    """Programa aviso post-respuesta para recalcular precios sugeridos en la store."""
    background_tasks.add_task(manager.broadcast_catalog_event, event, data)


@router.get("/", response_model=list[IngredienteRead], status_code=status.HTTP_200_OK)
def listar_ingredientes(
    uow: UowDep,
    incluir_eliminados: Annotated[bool, Query()] = False,
    search: Annotated[str | None, Query(max_length=100)] = None,
    es_alergeno: Annotated[bool | None, Query()] = None,
    unidad_medida_id: Annotated[int | None, Query(ge=1)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[IngredienteRead]:
    return ingrediente_service.listar(
        uow,
        incluir_eliminados=incluir_eliminados,
        search=search,
        es_alergeno=es_alergeno,
        unidad_medida_id=unidad_medida_id,
        page=page,
        size=size,
    )


@router.get("/{ingrediente_id}", response_model=IngredienteRead, status_code=status.HTTP_200_OK)
def obtener_ingrediente(
    uow: UowDep,
    ingrediente_id: int = Path(..., ge=1),
) -> IngredienteRead:
    return ingrediente_service.obtener_por_id(uow, ingrediente_id)


@router.post("/", response_model=IngredienteRead, status_code=status.HTTP_201_CREATED)
def crear_ingrediente(payload: IngredienteCreate, uow: UowDep, _admin: AdminDep, background_tasks: BackgroundTasks) -> IngredienteRead:
    ingrediente = ingrediente_service.crear(uow, payload)
    _avisar_catalogo(background_tasks, "CATALOG_INGREDIENT_CREATED", ingrediente_id=ingrediente.id)
    return ingrediente


@router.put("/{ingrediente_id}", response_model=IngredienteRead, status_code=status.HTTP_200_OK)
def actualizar_ingrediente(
    payload: IngredienteUpdate,
    uow: UowDep,
    _admin: AdminDep,
    background_tasks: BackgroundTasks,
    ingrediente_id: int = Path(..., ge=1),
) -> IngredienteRead:
    ingrediente = ingrediente_service.actualizar(uow, ingrediente_id, payload)
    _avisar_catalogo(background_tasks, "CATALOG_INGREDIENT_UPDATED", ingrediente_id=ingrediente.id)
    return ingrediente


@router.patch("/{ingrediente_id}/activar", response_model=IngredienteRead, status_code=status.HTTP_200_OK)
def activar_ingrediente(
    uow: UowDep,
    _admin: AdminDep,
    background_tasks: BackgroundTasks,
    ingrediente_id: int = Path(..., ge=1),
) -> IngredienteRead:
    ingrediente = ingrediente_service.activar(uow, ingrediente_id)
    _avisar_catalogo(background_tasks, "CATALOG_INGREDIENT_UPDATED", ingrediente_id=ingrediente.id)
    return ingrediente


@router.delete("/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ingrediente(
    uow: UowDep,
    _admin: AdminDep,
    background_tasks: BackgroundTasks,
    ingrediente_id: int = Path(..., ge=1),
) -> Response:
    ingrediente_service.eliminar(uow, ingrediente_id)
    _avisar_catalogo(background_tasks, "CATALOG_INGREDIENT_DELETED", ingrediente_id=ingrediente_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
