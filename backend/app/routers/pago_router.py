import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.core.auth_dependencies import get_current_user
from app.core.config import get_settings
from app.core.websocket import manager
from app.models.usuario import Usuario
from app.schemas.pago_schema import (
    ConfirmarPagoRequest,
    CrearPagoRequest,
    PagoCrearResponse,
    PagoEstadoResponse,
)
from app.services import pago_service
from app.uow.unit_of_work import SQLModelUnitOfWork, get_uow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pagos", tags=["Pagos MercadoPago"])

UowDep = Annotated[SQLModelUnitOfWork, Depends(get_uow)]
CurrentUserDep = Annotated[Usuario, Depends(get_current_user)]


def _build_payment_event(uow: SQLModelUnitOfWork, result: dict) -> dict | None:
    pedido_id = result.get("pedido_id")
    if not pedido_id:
        return None

    pedido = uow.pedidos.get_active_with_details(int(pedido_id))
    return {
        "pedido_id": int(pedido_id),
        "usuario_id": pedido.usuario_id if pedido else None,
        "new_state": result.get("pedido_estado") or (pedido.estado_codigo if pedido else None),
        "payment_state": result.get("estado"),
        "changed_by": None,
    }


@router.post("/create-preference", response_model=PagoCrearResponse)
def create_preference(
    payload: CrearPagoRequest,
    uow: UowDep,
    usuario: CurrentUserDep,
):
    return pago_service.crear_pago(uow, usuario, payload.pedido_id)


@router.post("/crear", response_model=PagoCrearResponse)
def crear_pago_alias_tpi(
    payload: CrearPagoRequest,
    uow: UowDep,
    usuario: CurrentUserDep,
):
    """Alias compatible con la especificación del TPI."""
    return pago_service.crear_pago(uow, usuario, payload.pedido_id)


@router.post("/webhook")
async def webhook(
    request: Request,
    uow: UowDep,
):
    """Webhook de MercadoPago.

    No requiere usuario autenticado porque MercadoPago lo llama directamente.
    El webhook actualiza el pago consultando la API oficial de MercadoPago.
    Si el pago queda aprobado, confirma el pedido y descuenta stock dentro de
    la misma transacción. Los eventos WebSocket se emiten después del commit.
    """

    try:
        query_params = dict(request.query_params)

        if request.headers.get("content-type", "").startswith("application/json"):
            data = await request.json()
        else:
            data = dict(await request.form())

        if not pago_service.validar_firma_webhook(dict(request.headers), query_params):
            logger.warning("Firma de webhook MercadoPago inválida")
            return {"status": "error", "reason": "Invalid webhook signature"}

        result = pago_service.procesar_webhook(uow, data, query_params=query_params)
        evento = _build_payment_event(uow, result) if result.get("status") == "processed" else None

        if evento:
            uow.session.commit()
            await manager.broadcast_order_event("ORDER_PAYMENT_UPDATED", evento)
            if evento["new_state"] == "CONFIRMADO":
                await manager.broadcast_order_event("ORDER_STATE_CHANGED", evento)

        return result
    except Exception as e:
        logger.exception("Error en webhook MP")
        return {"status": "error", "reason": str(e)}


@router.post("/confirm", response_model=PagoEstadoResponse)
async def confirm_payment(
    payload: ConfirmarPagoRequest,
    uow: UowDep,
    usuario: CurrentUserDep,
):
    result = pago_service.confirmar_pago(uow, usuario, payload.pedido_id, payload.payment_id)

    evento = {
        "pedido_id": result.pedido_id,
        "usuario_id": usuario.id,
        "new_state": result.pedido_estado,
        "payment_state": result.estado,
        "changed_by": usuario.id,
    }
    uow.session.commit()
    await manager.broadcast_order_event("ORDER_PAYMENT_UPDATED", evento)
    if result.pedido_estado == "CONFIRMADO":
        await manager.broadcast_order_event("ORDER_STATE_CHANGED", evento)

    return result


@router.get("/{pedido_id}", response_model=PagoEstadoResponse)
def obtener_pago_por_pedido(
    pedido_id: int,
    uow: UowDep,
    usuario: CurrentUserDep,
):
    return pago_service.obtener_pago_por_pedido(uow, usuario, pedido_id)


@router.get("/redirect/{pedido_id}/{status}")
async def redirect_after_pago(pedido_id: int, status: str, request: Request):
    settings = get_settings()
    frontend_url = settings.VITE_FRONTEND_URL or "http://127.0.0.1:5173"

    qs = request.url.query
    url = f"{frontend_url}/store/pedidos?pedido={pedido_id}&mp_status={status}"
    if qs:
        url += f"&{qs}"

    return RedirectResponse(url=url)
