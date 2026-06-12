import { create } from "zustand";

import type { PedidoWsEvent } from "../hooks/usePedidoWebSocket";

export type WsConnectionStatus = "connecting" | "connected" | "closed" | "error";

interface PedidoWsState {
  statusByChannel: Record<string, WsConnectionStatus>;
  lastEvent: PedidoWsEvent | null;
  eventCount: number;
  setStatus: (channel: string, status: WsConnectionStatus) => void;
  registerEvent: (event: PedidoWsEvent) => void;
  reset: () => void;
}

export const usePedidoWsStore = create<PedidoWsState>((set) => ({
  statusByChannel: {},
  lastEvent: null,
  eventCount: 0,
  setStatus: (channel, status) =>
    set((state) => ({
      statusByChannel: { ...state.statusByChannel, [channel]: status },
    })),
  registerEvent: (event) =>
    set((state) => ({
      lastEvent: event,
      eventCount: state.eventCount + 1,
    })),
  reset: () => set({ statusByChannel: {}, lastEvent: null, eventCount: 0 }),
}));
