import { useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { API_BASE_URL } from "../services/api";
import { getProductoById } from "../services/productoService";
import { useCarritoStore } from "../stores/carritoStore";

interface CatalogoWsEvent {
  event: string;
  timestamp?: string;
  data?: {
    producto_id?: number;
    ingrediente_id?: number;
    [key: string]: unknown;
  };
}

function buildCatalogoWsUrl() {
  return `${API_BASE_URL.replace(/^http/, "ws")}/ws/catalogo`;
}

export function useCatalogoWebSocket(enabled = true) {
  const queryClient = useQueryClient();
  const reconnectTimer = useRef<number | null>(null);
  const reconnectAttempt = useRef(0);
  const shouldReconnect = useRef(true);

  useEffect(() => {
    if (!enabled) return;

    shouldReconnect.current = true;
    let socket: WebSocket | null = null;

    async function sincronizarCarrito(productoIds?: number[]) {
      const { items, syncProducto, removeItem } = useCarritoStore.getState();
      const ids = productoIds?.length ? productoIds : items.map((item) => item.producto_id);

      await Promise.all(
        Array.from(new Set(ids)).map(async (productoId) => {
          try {
            const producto = await queryClient.fetchQuery({
              queryKey: ["producto", productoId],
              queryFn: () => getProductoById(productoId),
              staleTime: 0,
            });
            syncProducto(producto);
          } catch {
            removeItem(productoId);
          }
        }),
      );
    }

    function refrescarCatalogo(event?: CatalogoWsEvent) {
      void queryClient.invalidateQueries({ queryKey: ["productos"] });
      void queryClient.invalidateQueries({ queryKey: ["ingredientes"] });

      const productoId = event?.data?.producto_id;
      if (typeof productoId === "number") {
        void queryClient.invalidateQueries({ queryKey: ["producto", productoId] });
        void sincronizarCarrito([productoId]);
      } else {
        void queryClient.invalidateQueries({ queryKey: ["producto"] });
        void sincronizarCarrito();
      }
    }

    function connect() {
      socket = new WebSocket(buildCatalogoWsUrl());

      socket.onopen = () => {
        reconnectAttempt.current = 0;
      };

      socket.onmessage = (message) => {
        try {
          refrescarCatalogo(JSON.parse(message.data) as CatalogoWsEvent);
        } catch {
          refrescarCatalogo();
        }
      };

      socket.onclose = () => {
        if (shouldReconnect.current) {
          const delay = Math.min(30000, 1000 * 2 ** reconnectAttempt.current);
          reconnectAttempt.current += 1;
          reconnectTimer.current = window.setTimeout(connect, delay);
        }
      };
    }

    connect();

    const syncInterval = window.setInterval(() => {
      void sincronizarCarrito();
    }, 15000);

    return () => {
      window.clearInterval(syncInterval);
      shouldReconnect.current = false;
      if (reconnectTimer.current !== null) {
        window.clearTimeout(reconnectTimer.current);
      }
      socket?.close();
    };
  }, [enabled, queryClient]);
}
