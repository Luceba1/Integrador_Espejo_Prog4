import { create } from "zustand";

interface PagoUiState {
  pedidoIdEnPago: number | null;
  estadoPago: "idle" | "creating_preference" | "redirecting" | "confirming" | "confirmed" | "error";
  mensaje: string | null;
  setPagoPendiente: (pedidoId: number) => void;
  setEstadoPago: (estado: PagoUiState["estadoPago"], mensaje?: string | null) => void;
  resetPago: () => void;
}

export const usePagoStore = create<PagoUiState>((set) => ({
  pedidoIdEnPago: null,
  estadoPago: "idle",
  mensaje: null,
  setPagoPendiente: (pedidoId) => set({ pedidoIdEnPago: pedidoId, estadoPago: "creating_preference", mensaje: null }),
  setEstadoPago: (estado, mensaje = null) => set({ estadoPago: estado, mensaje }),
  resetPago: () => set({ pedidoIdEnPago: null, estadoPago: "idle", mensaje: null }),
}));
