from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from app.core.auth_dependencies import require_roles
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
    producto_id: int = Path(..., ge=1),
) -> ProductoIngredienteRead:
    return producto_service.asociar_ingrediente_producto(uow, producto_id, payload)


@router.patch(
    "/{producto_id}/imagenes",
    response_model=ProductoReadDetail,
    status_code=status.HTTP_200_OK,
)
def actualizar_imagenes_producto(
    payload: ImagenProductoUpdate,
    uow: UowDep,
    _admin: AdminDep,
    producto_id: int = Path(..., ge=1),
) -> ProductoReadDetail:
    return producto_service.actualizar_imagenes(uow, producto_id, payload.imagenes_url)


@router.get("/{producto_id}", response_model=ProductoReadDetail, status_code=status.HTTP_200_OK)
def obtener_producto(
    uow: UowDep,
    producto_id: int = Path(..., ge=1),
) -> ProductoReadDetail:
    return producto_service.obtener_por_id(uow, producto_id)


@router.post("/", response_model=ProductoReadDetail, status_code=status.HTTP_201_CREATED)
def crear_producto(payload: ProductoCreate, uow: UowDep, _admin: AdminDep) -> ProductoReadDetail:
    return producto_service.crear(uow, payload)


@router.put("/{producto_id}", response_model=ProductoReadDetail, status_code=status.HTTP_200_OK)
def actualizar_producto(
    payload: ProductoUpdate,
    uow: UowDep,
    _admin: AdminDep,
    producto_id: int = Path(..., ge=1),
) -> ProductoReadDetail:
    return producto_service.actualizar(uow, producto_id, payload)


@router.patch(
    "/{producto_id}/disponibilidad",
    response_model=ProductoReadDetail,
    status_code=status.HTTP_200_OK,
)
def cambiar_disponibilidad_producto(
    payload: ProductoDisponibilidadUpdate,
    uow: UowDep,
    _usuario: AdminStockDep,
    producto_id: int = Path(..., ge=1),
) -> ProductoReadDetail:
    return producto_service.cambiar_disponibilidad(uow, producto_id, payload.disponible)


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
    producto_id: int = Path(..., ge=1),
) -> ProductoReadDetail:
    return producto_service.activar(uow, producto_id)


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    uow: UowDep,
    _admin: AdminDep,
    producto_id: int = Path(..., ge=1),
) -> Response:
    producto_service.eliminar(uow, producto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
