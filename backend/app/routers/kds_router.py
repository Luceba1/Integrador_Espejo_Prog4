from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status

from app.core.auth_dependencies import require_roles
from app.core.security import decode_access_token
from app.core.websocket import manager
from app.models.usuario import Usuario
from app.services import auth_service, pedido_service
from app.uow.unit_of_work import SQLModelUnitOfWork, get_uow

router = APIRouter(prefix="/cocina", tags=["KDS / WebSockets"])

ROLES_KDS = {"ADMIN", "PEDIDOS"}
KDSUserDep = Annotated[Usuario, Depends(require_roles("ADMIN", "PEDIDOS"))]
UowDep = Annotated[SQLModelUnitOfWork, Depends(get_uow)]
ESTADOS_COCINA = {"PENDIENTE", "CONFIRMADO", "EN_PREP"}


def _extraer_token_ws(websocket: WebSocket, token_query: str | None) -> str | None:
    """Obtiene el token desde cookie HttpOnly o desde query param para pruebas."""

    token = websocket.cookies.get("access_token") or token_query
    if not token:
        return None
    if token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1]
    return token.strip()


def _validar_usuario_ws(token: str) -> Usuario:
    try:
        payload = decode_access_token(token)
        usuario_id = int(payload.get("sub"))
    except (jwt.InvalidTokenError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o vencido.") from exc

    with SQLModelUnitOfWork() as uow:
        usuario = uow.usuarios.get_active_by_id(usuario_id)
        if usuario is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inválido o inactivo.")
        roles = set(auth_service.roles_codigos(usuario))
        if not roles.intersection(ROLES_KDS):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permisos insuficientes para KDS.")
        return usuario


@router.get("/pedidos")
def listar_pedidos_cocina(
    uow: UowDep,
    usuario: KDSUserDep,
):
    """Listado REST de respaldo para KDS si el WebSocket se desconecta.

    El frontend puede consultar este endpoint cada 5-10 segundos como fallback.
    Acepta la cookie HttpOnly del login normal o Authorization: Bearer para pruebas.
    """

    pedidos = pedido_service.listar(uow, usuario=usuario, page=1, size=50)
    return [pedido for pedido in pedidos if pedido.estado_codigo in ESTADOS_COCINA]


@router.websocket("/ws")
async def websocket_kds(websocket: WebSocket, token: str | None = None):
    """Canal WebSocket autenticado para el Display de Cocina.

    Seguridad del handshake:
    1. Lee JWT desde cookie HttpOnly access_token o query ?token=... para pruebas.
    2. Valida firma y expiración antes de aceptar la conexión.
    3. Verifica usuario activo y rol ADMIN/PEDIDOS.
    4. Recién después llama a manager.connect(websocket), que ejecuta ws.accept().
    """

    raw_token = _extraer_token_ws(websocket, token)
    if not raw_token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token de autenticación requerido")
        return

    try:
        _validar_usuario_ws(raw_token)
    except HTTPException as exc:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=str(exc.detail))
        return

    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:  # noqa: BLE001 - evita que una desconexión brusca rompa broadcasts futuros
        manager.disconnect(websocket)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
