from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status

from app.core.websocket import manager
from app.core.ws_auth import (
    ROLES_GESTION_PEDIDOS,
    extraer_token_ws,
    validar_acceso_pedido_ws,
    validar_usuario_ws,
)
from app.uow.unit_of_work import SQLModelUnitOfWork

router = APIRouter(prefix="/ws", tags=["WebSockets"])


async def _cerrar_por_http_exception(websocket: WebSocket, exc: HTTPException) -> None:
    await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=str(exc.detail))


async def _websocket_admin_feed(websocket: WebSocket, token: str | None = None):
    """Canal de administración para ADMIN/PEDIDOS.

    Recibe eventos de creación, cancelación, pago y cambio de estado de cualquier pedido.
    Se reutiliza en varios paths para compatibilidad con el TPI y con el frontend.
    """

    raw_token = extraer_token_ws(websocket, token)
    if not raw_token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token de autenticación requerido")
        return

    try:
        validar_usuario_ws(raw_token, roles_permitidos=ROLES_GESTION_PEDIDOS)
    except HTTPException as exc:
        await _cerrar_por_http_exception(websocket, exc)
        return

    await manager.connect_admin(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:  # noqa: BLE001
        manager.disconnect(websocket)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


@router.websocket("/admin")
async def websocket_admin(websocket: WebSocket, token: str | None = None):
    await _websocket_admin_feed(websocket, token)


@router.websocket("/pedidos")
async def websocket_pedidos_tpi(websocket: WebSocket, token: str | None = None):
    """Alias TPI: feed de todos los pedidos para ADMIN/PEDIDOS."""
    await _websocket_admin_feed(websocket, token)


@router.websocket("/admin/pedidos")
async def websocket_admin_pedidos_tpi(websocket: WebSocket, token: str | None = None):
    """Alias TPI/documentación: canal admin de pedidos."""
    await _websocket_admin_feed(websocket, token)


@router.websocket("/mis-pedidos")
async def websocket_mis_pedidos(websocket: WebSocket, token: str | None = None):
    """Canal privado del cliente autenticado.

    Recibe eventos solo de pedidos cuyo usuario_id coincide con el usuario autenticado.
    """

    raw_token = extraer_token_ws(websocket, token)
    if not raw_token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token de autenticación requerido")
        return

    try:
        usuario = validar_usuario_ws(raw_token)
    except HTTPException as exc:
        await _cerrar_por_http_exception(websocket, exc)
        return

    await manager.connect_user(websocket, usuario.id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:  # noqa: BLE001
        manager.disconnect(websocket)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


@router.websocket("/pedidos/{pedido_id}")
async def websocket_pedido(websocket: WebSocket, pedido_id: int, token: str | None = None):
    """Canal puntual de seguimiento de un pedido.

    Lo puede abrir el dueño del pedido o un usuario ADMIN/PEDIDOS.
    """

    raw_token = extraer_token_ws(websocket, token)
    if not raw_token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token de autenticación requerido")
        return

    try:
        usuario = validar_usuario_ws(raw_token)
        with SQLModelUnitOfWork() as uow:
            pedido = uow.pedidos.get_active_with_details(pedido_id)
            validar_acceso_pedido_ws(usuario, pedido)
    except HTTPException as exc:
        await _cerrar_por_http_exception(websocket, exc)
        return

    await manager.connect_order(websocket, pedido_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:  # noqa: BLE001
        manager.disconnect(websocket)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


@router.websocket("/catalogo")
async def websocket_catalogo(websocket: WebSocket):
    """Canal público de catálogo.

    La store lo usa para invalidar productos cuando administración cambia precios,
    ingredientes, disponibilidad o recetas. No expone datos privados: solo avisa
    que el catálogo debe refrescarse.
    """
    await manager.connect_catalog(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:  # noqa: BLE001
        manager.disconnect(websocket)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
