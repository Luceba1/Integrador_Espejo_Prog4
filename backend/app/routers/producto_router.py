from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Path, Query, Response, status

from app.core.auth_dependencies import require_roles
from app.core.websocket import manager
from app.models.usuario import Usuario
from app.schemas.producto_schema import (
    ImagenProductoUpdate,
    ProductoCreate,
    ProductoDisponibilidadUpdate,
    ProductoIngredientePayload,
    ProductoIngredienteRead,
    ProductoReadDetail,
    ProductoStockUpdate,
    ProductoUpdate,
)
from app.services import producto_service
from app.uow.unit_of_work import SQLModelUnitOfWork, get_uow

router = APIRouter(prefix="/productos", tags=["Productos"])

UowDep = Annotated[SQLModelUnitOfWork, Depends(get_uow)]
AdminDep = Annotated[Usuario, Depends(require_roles("ADMIN"))]
AdminStockDep = Annotated[Usuario, Depends(require_roles("ADMIN", "STOCK"))]


def _avisar_catalogo(background_tasks: BackgroundTasks, event: str, **data: object) -> None:
    """Programa aviso post-respuesta para que la store refresque sin F5."""
    background_tasks.add_task(manager.broadcast_catalog_event, event, data)


@router.get("/", response_model=list[ProductoReadDetail], status_code=status.HTTP_200_OK)
def listar_productos(
    uow: UowDep,
    search: Annotated[str | None, Query(max_length=100)] = None,
    categoria_id: Annotated[int | None, Query(ge=1)] = None,
    disponible: Annotated[bool | None, Query()] = None,
    incluir_eliminados: Annotated[bool, Query()] = False,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[ProductoReadDetail]:
    return producto_service.listar(
        uow,
        search=search,
        categoria_id=categoria_id,
        disponible=disponible,
        incluir_eliminados=incluir_eliminados,
        page=page,
        size=size,
    )


@router.get(
    "/{producto_id}/ingredientes",
    response_model=list[ProductoIngredienteRead],
    status_code=status.HTTP_200_OK,
)
def listar_ingredientes_producto(
    uow: UowDep,
    producto_id: int = Path(..., ge=1),
) -> list[ProductoIngredienteRead]:
    return producto_service.listar_ingredientes_producto(uow, producto_id)


@router.post(
    "/{producto_id}/ingredientes",
    response_model=ProductoIngredienteRead,
    status_code=status.HTTP_201_CREATED,
)
def asociar_ingrediente_producto(
    payload: ProductoIngredientePayload,
    uow: UowDep,
    _admin: AdminDep,
    background_tasks: BackgroundTasks,
    producto_id: int = Path(..., ge=1),
) -> ProductoIngredienteRead:
    resultado = producto_service.asociar_ingrediente_producto(uow, producto_id, payload)
    _avisar_catalogo(background_tasks, "CATALOG_PRODUCT_UPDATED", producto_id=producto_id)
    return resultado


@router.patch(
    "/{producto_id}/imagenes",
    response_model=ProductoReadDetail,
    status_code=status.HTTP_200_OK,
)
def actualizar_imagenes_producto(
    payload: ImagenProductoUpdate,
    uow: UowDep,
    _admin: AdminDep,
    background_tasks: BackgroundTasks,
    producto_id: int = Path(..., ge=1),
) -> ProductoReadDetail:
    producto = producto_service.actualizar_imagenes(uow, producto_id, payload.imagenes_url)
    _avisar_catalogo(background_tasks, "CATALOG_PRODUCT_UPDATED", producto_id=producto.id)
    return producto


@router.get("/{producto_id}", response_model=ProductoReadDetail, status_code=status.HTTP_200_OK)
def obtener_producto(
    uow: UowDep,
    producto_id: int = Path(..., ge=1),
) -> ProductoReadDetail:
    return producto_service.obtener_por_id(uow, producto_id)


@router.post("/", response_model=ProductoReadDetail, status_code=status.HTTP_201_CREATED)
def crear_producto(payload: ProductoCreate, uow: UowDep, _admin: AdminDep, background_tasks: BackgroundTasks) -> ProductoReadDetail:
    producto = producto_service.crear(uow, payload)
    _avisar_catalogo(background_tasks, "CATALOG_PRODUCT_CREATED", producto_id=producto.id)
    return producto


@router.put("/{producto_id}", response_model=ProductoReadDetail, status_code=status.HTTP_200_OK)
def actualizar_producto(
    payload: ProductoUpdate,
    uow: UowDep,
    _admin: AdminDep,
    background_tasks: BackgroundTasks,
    producto_id: int = Path(..., ge=1),
) -> ProductoReadDetail:
    producto = producto_service.actualizar(uow, producto_id, payload)
    _avisar_catalogo(background_tasks, "CATALOG_PRODUCT_UPDATED", producto_id=producto.id)
    return producto


@router.patch(
    "/{producto_id}/disponibilidad",
    response_model=ProductoReadDetail,
    status_code=status.HTTP_200_OK,
)
def cambiar_disponibilidad_producto(
    payload: ProductoDisponibilidadUpdate,
    uow: UowDep,
    _usuario: AdminStockDep,
    background_tasks: BackgroundTasks,
    producto_id: int = Path(..., ge=1),
) -> ProductoReadDetail:
    producto = producto_service.cambiar_disponibilidad(uow, producto_id, payload.disponible)
    _avisar_catalogo(background_tasks, "CATALOG_PRODUCT_UPDATED", producto_id=producto.id)
    return producto


@router.patch(
    "/{producto_id}/stock",
    response_model=ProductoReadDetail,
    status_code=status.HTTP_200_OK,
)
def actualizar_stock_producto(
    payload: ProductoStockUpdate,
    uow: UowDep,
    _usuario: AdminStockDep,
    producto_id: int = Path(..., ge=1),
) -> ProductoReadDetail:
    return producto_service.actualizar_stock(uow, producto_id, payload.stock_cantidad)


@router.patch("/{producto_id}/activar", response_model=ProductoReadDetail, status_code=status.HTTP_200_OK)
def activar_producto(
    uow: UowDep,
    _admin: AdminDep,
    background_tasks: BackgroundTasks,
    producto_id: int = Path(..., ge=1),
) -> ProductoReadDetail:
    producto = producto_service.activar(uow, producto_id)
    _avisar_catalogo(background_tasks, "CATALOG_PRODUCT_UPDATED", producto_id=producto.id)
    return producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    uow: UowDep,
    _admin: AdminDep,
    background_tasks: BackgroundTasks,
    producto_id: int = Path(..., ge=1),
) -> Response:
    producto_service.eliminar(uow, producto_id)
    _avisar_catalogo(background_tasks, "CATALOG_PRODUCT_DELETED", producto_id=producto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
