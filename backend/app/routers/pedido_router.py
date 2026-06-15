from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.core.auth_dependencies import get_current_user, require_roles
from app.core.websocket import manager
from app.models.usuario import Usuario
from app.schemas.pedido_schema import (
    EstadoPedidoRead,
    FormaPagoRead,
    PedidoCancelacion,
    PedidoCreate,
    PedidoEstadoUpdate,
    PedidoRead,
)
from app.services import pedido_service
from app.uow.unit_of_work import SQLModelUnitOfWork, get_uow

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

UowDep = Annotated[SQLModelUnitOfWork, Depends(get_uow)]
CurrentUserDep = Annotated[Usuario, Depends(get_current_user)]
AdminPedidosDep = Annotated[Usuario, Depends(require_roles("ADMIN", "PEDIDOS"))]


@router.get("/estados", response_model=list[EstadoPedidoRead], status_code=status.HTTP_200_OK)
def listar_estados_pedido(uow: UowDep, _usuario: CurrentUserDep) -> list[EstadoPedidoRead]:
    return uow.estados_pedido.list_active()


@router.get("/formas-pago", response_model=list[FormaPagoRead], status_code=status.HTTP_200_OK)
def listar_formas_pago(uow: UowDep, _usuario: CurrentUserDep) -> list[FormaPagoRead]:
    return uow.formas_pago.list_active()


@router.get("/", response_model=list[PedidoRead], status_code=status.HTTP_200_OK)
def listar_pedidos(
    uow: UowDep,
    usuario: CurrentUserDep,
    estado_codigo: Annotated[str | None, Query(max_length=40)] = None,
    usuario_id: Annotated[int | None, Query(ge=1)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[PedidoRead]:
    return pedido_service.listar(
        uow,
        usuario=usuario,
        estado_codigo=estado_codigo,
        usuario_id=usuario_id,
        page=page,
        size=size,
    )


@router.post("/", response_model=PedidoRead, status_code=status.HTTP_201_CREATED)
async def crear_pedido(
    payload: PedidoCreate,
    usuario: CurrentUserDep,
) -> PedidoRead:
    with SQLModelUnitOfWork() as uow:
        pedido = pedido_service.crear_desde_carrito(uow, usuario, payload)
        evento = {
            "pedido_id": pedido.id,
            "usuario_id": pedido.usuario_id,
            "new_state": pedido.estado_codigo,
            "old_state": None,
            "changed_by": usuario.id,
        }

    # El commit ya fue ejecutado por el UoW. El broadcast queda post-commit.
    await manager.broadcast_order_event("ORDER_CREATED", evento)
    return pedido


@router.get("/{pedido_id}", response_model=PedidoRead, status_code=status.HTTP_200_OK)
def obtener_pedido(
    uow: UowDep,
    usuario: CurrentUserDep,
    pedido_id: int = Path(..., ge=1),
) -> PedidoRead:
    return pedido_service.obtener_por_id(uow, pedido_id, usuario)


@router.patch("/{pedido_id}/estado", response_model=PedidoRead, status_code=status.HTTP_200_OK)
async def avanzar_estado_pedido(
    payload: PedidoEstadoUpdate,
    usuario: AdminPedidosDep,
    pedido_id: int = Path(..., ge=1),
) -> PedidoRead:
    with SQLModelUnitOfWork() as uow:
        pedido_actual = pedido_service.obtener_por_id(uow, pedido_id, usuario)
        estado_anterior = pedido_actual.estado_codigo
        pedido = pedido_service.avanzar_estado(
            uow,
            pedido_id=pedido_id,
            nuevo_estado_codigo=payload.estado_codigo,
            usuario=usuario,
            motivo=payload.motivo,
            recuperar_stock=payload.recuperar_stock,
        )
        evento = {
            "pedido_id": pedido.id,
            "usuario_id": pedido.usuario_id,
            "new_state": pedido.estado_codigo,
            "old_state": estado_anterior,
            "changed_by": usuario.id,
            "motivo": payload.motivo,
        }

    # El commit ya fue ejecutado por el UoW. El broadcast queda post-commit.
    await manager.broadcast_order_event("ORDER_STATE_CHANGED", evento)
    return pedido


@router.patch("/{pedido_id}/cancelar", response_model=PedidoRead, status_code=status.HTTP_200_OK)
async def cancelar_pedido_propio(
    payload: PedidoCancelacion,
    usuario: CurrentUserDep,
    pedido_id: int = Path(..., ge=1),
) -> PedidoRead:
    with SQLModelUnitOfWork() as uow:
        pedido_actual = pedido_service.obtener_por_id(uow, pedido_id, usuario)
        estado_anterior = pedido_actual.estado_codigo
        pedido = pedido_service.cancelar_propio(
            uow,
            pedido_id=pedido_id,
            usuario=usuario,
            motivo=payload.motivo,
        )
        evento = {
            "pedido_id": pedido.id,
            "usuario_id": pedido.usuario_id,
            "new_state": pedido.estado_codigo,
            "old_state": estado_anterior,
            "changed_by": usuario.id,
            "motivo": payload.motivo,
        }

    # El commit ya fue ejecutado por el UoW. El broadcast queda post-commit.
    await manager.broadcast_order_event("ORDER_STATE_CHANGED", evento)
    return pedido


@router.delete("/{pedido_id}", response_model=PedidoRead, status_code=status.HTTP_200_OK)
async def cancelar_pedido_alias_tpi(
    usuario: CurrentUserDep,
    pedido_id: int = Path(..., ge=1),
    motivo: str = Query(default="Cancelación solicitada por el cliente.", min_length=3, max_length=255),
) -> PedidoRead:
    with SQLModelUnitOfWork() as uow:
        pedido_actual = pedido_service.obtener_por_id(uow, pedido_id, usuario)
        estado_anterior = pedido_actual.estado_codigo
        pedido = pedido_service.cancelar_propio(
            uow,
            pedido_id=pedido_id,
            usuario=usuario,
            motivo=motivo,
        )
        evento = {
            "pedido_id": pedido.id,
            "usuario_id": pedido.usuario_id,
            "new_state": pedido.estado_codigo,
            "old_state": estado_anterior,
            "changed_by": usuario.id,
            "motivo": motivo,
        }

    # El commit ya fue ejecutado por el UoW. El broadcast queda post-commit.
    await manager.broadcast_order_event("ORDER_STATE_CHANGED", evento)
    return pedido
