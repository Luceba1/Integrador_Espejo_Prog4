"""WebSocket Manager para eventos en tiempo real de pedidos.

El estado real del pedido vive en PostgreSQL. Este manager solo mantiene
conexiones activas y difunde eventos livianos después de que la transacción ya
fue confirmada.

Canales soportados:
- admin: paneles ADMIN/PEDIDOS que necesitan ver todos los pedidos.
- user:{usuario_id}: clientes autenticados que quieren actualizar su listado.
- order:{pedido_id}: seguimiento puntual de un pedido.
- legacy: compatibilidad con /cocina/ws de fases anteriores.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from collections import defaultdict
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger("app.core.websocket")


class ConnectionManager:
    """Administra conexiones WebSocket por canal y difunde eventos JSON."""

    def __init__(self) -> None:
        self.active_connections: set[WebSocket] = set()  # compatibilidad /cocina/ws
        self.admin_connections: set[WebSocket] = set()
        self.user_connections: dict[int, set[WebSocket]] = defaultdict(set)
        self.order_connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, websocket: WebSocket) -> None:
        """Canal legacy usado por /cocina/ws."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info("Nueva conexión WebSocket legacy. Total: %s", len(self.active_connections))

    def disconnect(self, websocket: WebSocket) -> None:
        """Desconecta un socket de cualquier canal donde esté registrado."""
        self.active_connections.discard(websocket)
        self.admin_connections.discard(websocket)

        for pedido_id in list(self.order_connections.keys()):
            self.order_connections[pedido_id].discard(websocket)
            if not self.order_connections[pedido_id]:
                self.order_connections.pop(pedido_id, None)

        for usuario_id in list(self.user_connections.keys()):
            self.user_connections[usuario_id].discard(websocket)
            if not self.user_connections[usuario_id]:
                self.user_connections.pop(usuario_id, None)

        logger.info("Conexión WebSocket finalizada.")

    async def connect_admin(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.admin_connections.add(websocket)
        logger.info("Nueva conexión WebSocket admin. Total admin: %s", len(self.admin_connections))

    async def connect_user(self, websocket: WebSocket, usuario_id: int) -> None:
        await websocket.accept()
        self.user_connections[usuario_id].add(websocket)
        logger.info(
            "Nueva conexión WebSocket usuario %s. Total usuario: %s",
            usuario_id,
            len(self.user_connections[usuario_id]),
        )

    async def connect_order(self, websocket: WebSocket, pedido_id: int) -> None:
        await websocket.accept()
        self.order_connections[pedido_id].add(websocket)
        logger.info(
            "Nueva conexión WebSocket pedido %s. Total pedido: %s",
            pedido_id,
            len(self.order_connections[pedido_id]),
        )

    async def _send_to_many(self, connections: set[WebSocket], payload: dict[str, Any]) -> None:
        if not connections:
            return

        for connection in list(connections):
            try:
                await connection.send_json(payload)
            except Exception as exc:  # noqa: BLE001 - robustez ante desconexiones bruscas
                logger.warning("Error enviando evento WebSocket. Se remueve conexión: %s", exc)
                self.disconnect(connection)

    async def broadcast(self, event: str, data: dict[str, Any]) -> None:
        """Broadcast legacy a /cocina/ws."""
        payload = {"event": event, "data": data}
        await self._send_to_many(self.active_connections, payload)

    def _build_order_payload(self, event: str, data: dict[str, Any]) -> dict[str, Any]:
        """Normaliza eventos al contrato WebSocket del TPI sin perder compatibilidad.

        El PDF documenta eventos con campos `estado_nuevo`, `estado_anterior`,
        `pedido_id`, `usuario_id`, `motivo` y `timestamp`. El frontend anterior
        también usaba `new_state` y `changed_by`, por eso conservamos ambos.
        """

        event_map = {
            "ORDER_CREATED": "pedido_creado",
            "ORDER_STATE_CHANGED": "estado_cambiado",
            "ORDER_PAYMENT_UPDATED": "pago_confirmado" if data.get("new_state") == "CONFIRMADO" else "pago_actualizado",
        }
        normalized = dict(data)
        normalized.setdefault("estado_nuevo", normalized.get("new_state"))
        normalized.setdefault("estado_anterior", normalized.get("old_state"))
        normalized.setdefault("usuario_id", normalized.get("changed_by"))
        normalized.setdefault("motivo", None)
        normalized.setdefault("timestamp", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

        return {
            "event": event_map.get(event, event),
            "event_original": event,
            "pedido_id": normalized.get("pedido_id"),
            "usuario_id": normalized.get("usuario_id"),
            "estado_anterior": normalized.get("estado_anterior"),
            "estado_nuevo": normalized.get("estado_nuevo"),
            "motivo": normalized.get("motivo"),
            "timestamp": normalized.get("timestamp"),
            "data": normalized,
        }

    async def broadcast_admin(self, event: str, data: dict[str, Any]) -> None:
        payload = self._build_order_payload(event, data)
        await self._send_to_many(self.admin_connections, payload)

    async def broadcast_user(self, usuario_id: int | None, event: str, data: dict[str, Any]) -> None:
        if usuario_id is None:
            return
        payload = self._build_order_payload(event, data)
        await self._send_to_many(self.user_connections.get(usuario_id, set()), payload)

    async def broadcast_order(self, pedido_id: int | None, event: str, data: dict[str, Any]) -> None:
        if pedido_id is None:
            return
        payload = self._build_order_payload(event, data)
        await self._send_to_many(self.order_connections.get(pedido_id, set()), payload)

    async def broadcast_order_event(self, event: str, data: dict[str, Any]) -> None:
        """Emite un evento de pedido a todos los canales relevantes.

        data debería incluir pedido_id y, si está disponible, usuario_id.
        """
        pedido_id = data.get("pedido_id")
        usuario_id = data.get("usuario_id")

        await self.broadcast_admin(event, data)
        await self.broadcast_user(usuario_id, event, data)
        await self.broadcast_order(pedido_id, event, data)
        # Compatibilidad con pantalla KDS anterior.
        await self.broadcast(event, data)


manager = ConnectionManager()
