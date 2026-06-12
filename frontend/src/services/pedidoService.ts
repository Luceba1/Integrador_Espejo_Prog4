import { api } from "./api";
import type { EstadoPedido, FormaPago, Pedido, PedidoCreatePayload, PedidoEstadoUpdatePayload } from "../types/pedido";

export async function getPedidos(params: {
  estado_codigo?: string;
  usuario_id?: number;
  page?: number;
  size?: number;
}) {
  const response = await api.get<Pedido[]>("/pedidos/", { params });
  return response.data;
}

export async function getEstadosPedido() {
  const response = await api.get<EstadoPedido[]>("/pedidos/estados");
  return response.data;
}

export async function getFormasPago() {
  const response = await api.get<FormaPago[]>("/pedidos/formas-pago");
  return response.data;
}

export async function avanzarEstadoPedido(id: number, payload: PedidoEstadoUpdatePayload) {
  const response = await api.patch<Pedido>(`/pedidos/${id}/estado`, payload);
  return response.data;
}

export async function cancelarPedido(id: number, motivo?: string) {
  const response = await api.patch<Pedido>(`/pedidos/${id}/cancelar`, { motivo });
  return response.data;
}

export async function createPedido(payload: PedidoCreatePayload) {
  const response = await api.post<Pedido>("/pedidos/", payload);
  return response.data;
}
