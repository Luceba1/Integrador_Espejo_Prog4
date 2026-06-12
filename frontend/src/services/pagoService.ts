import { api } from "./api";
import type { PagoCrearResponse, PagoEstadoResponse } from "../types/pago";

export async function crearPreferenciaPago(pedidoId: number) {
  const response = await api.post<PagoCrearResponse>("/pagos/create-preference", {
    pedido_id: pedidoId,
  });
  return response.data;
}

export async function confirmarPagoMercadoPago(pedidoId: number, paymentId?: number | null) {
  const response = await api.post<PagoEstadoResponse>("/pagos/confirm", {
    pedido_id: pedidoId,
    payment_id: paymentId ?? null,
  });
  return response.data;
}
