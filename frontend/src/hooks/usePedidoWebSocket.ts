import { useEffect, useMemo, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { API_BASE_URL } from "../services/api";
import { usePedidoWsStore, type WsConnectionStatus } from "../stores/wsStore";

export type PedidoWebSocketMode = "admin" | "mis-pedidos" | "pedido";

export interface PedidoWsEvent {
  event: string;
  event_original?: string;
  pedido_id?: number;
  usuario_id?: number | null;
  estado_nuevo?: string | null;
  estado_anterior?: string | null;
  motivo?: string | null;
  timestamp?: string;
  data: {
    pedido_id?: number;
    usuario_id?: number | null;
    new_state?: string | null;
    estado_nuevo?: string | null;
    estado_anterior?: string | null;
    payment_state?: string | null;
    changed_by?: number | null;
    timestamp?: string;
    [key: string]: unknown;
  };
}

interface UsePedidoWebSocketOptions {
  mode: PedidoWebSocketMode;
  pedidoId?: number;
  enabled?: boolean;
}

function buildWsUrl(mode: PedidoWebSocketMode, pedidoId?: number) {
  const base = API_BASE_URL.replace(/^http/, "ws");

  if (mode === "admin") return `${base}/ws/admin`;
  if (mode === "mis-pedidos") return `${base}/ws/mis-pedidos`;
  if (!pedidoId) throw new Error("pedidoId es obligatorio para el modo pedido.");
  return `${base}/ws/pedidos/${pedidoId}`;
}

function channelKey(mode: PedidoWebSocketMode, pedidoId?: number) {
  return mode === "pedido" ? `pedido:${pedidoId ?? "none"}` : mode;
}

export function usePedidoWebSocket({ mode, pedidoId, enabled = true }: UsePedidoWebSocketOptions) {
  const queryClient = useQueryClient();
  const setWsStatus = usePedidoWsStore((state) => state.setStatus);
  const registerEvent = usePedidoWsStore((state) => state.registerEvent);
  const lastEvent = usePedidoWsStore((state) => state.lastEvent);
  const eventCount = usePedidoWsStore((state) => state.eventCount);
  const statusByChannel = usePedidoWsStore((state) => state.statusByChannel);
  const reconnectTimer = useRef<number | null>(null);
  const reconnectAttempt = useRef(0);
  const shouldReconnect = useRef(true);

  const wsUrl = useMemo(() => {
    if (!enabled) return null;
    if (mode === "pedido" && !pedidoId) return null;
    return buildWsUrl(mode, pedidoId);
  }, [enabled, mode, pedidoId]);

  const channel = useMemo(() => channelKey(mode, pedidoId), [mode, pedidoId]);
  const status: WsConnectionStatus = statusByChannel[channel] ?? "closed";

  useEffect(() => {
    if (!wsUrl) {
      setWsStatus(channel, "closed");
      return;
    }

    shouldReconnect.current = true;
    let socket: WebSocket | null = null;

    function connect() {
      setWsStatus(channel, "connecting");
      socket = new WebSocket(wsUrl!);

      socket.onopen = () => {
        reconnectAttempt.current = 0;
        setWsStatus(channel, "connected");
      };

      socket.onmessage = (message) => {
        try {
          const parsed = JSON.parse(message.data) as PedidoWsEvent;
          registerEvent(parsed);
          // La consigna pide invalidación/sincronización del estado servidor ante eventos WS.
          void queryClient.invalidateQueries({ queryKey: ["pedidos"] });
          void queryClient.invalidateQueries({ queryKey: ["admin", "dashboard"] });
        } catch {
          // Se ignoran mensajes no JSON para no cortar la conexión.
        }
      };

      socket.onerror = () => setWsStatus(channel, "error");

      socket.onclose = () => {
        setWsStatus(channel, "closed");
        if (shouldReconnect.current) {
          const delay = Math.min(30000, 1000 * 2 ** reconnectAttempt.current);
          reconnectAttempt.current += 1;
          reconnectTimer.current = window.setTimeout(connect, delay);
        }
      };
    }

    connect();

    return () => {
      shouldReconnect.current = false;
      if (reconnectTimer.current !== null) {
        window.clearTimeout(reconnectTimer.current);
      }
      socket?.close();
    };
  }, [wsUrl, channel, queryClient, registerEvent, setWsStatus]);

  return { status, lastEvent, eventCount };
}
