import { request } from "./api";
import type { UnidadMedida, UnidadMedidaPayload } from "../types/unidadMedida";

export function getUnidadesMedida(params?: { page?: number; size?: number; incluir_eliminadas?: boolean }) {
  const query = new URLSearchParams();
  if (params?.page) query.set("page", String(params.page));
  if (params?.size) query.set("size", String(params.size));
  if (typeof params?.incluir_eliminadas === "boolean") query.set("incluir_eliminadas", String(params.incluir_eliminadas));
  const suffix = query.toString();
  return request<UnidadMedida[]>(`/unidades-medida/${suffix ? `?${suffix}` : ""}`);
}

export function createUnidadMedida(payload: UnidadMedidaPayload) {
  return request<UnidadMedida>("/unidades-medida/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateUnidadMedida(id: number, payload: UnidadMedidaPayload) {
  return request<UnidadMedida>(`/unidades-medida/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteUnidadMedida(id: number) {
  return request<void>(`/unidades-medida/${id}`, {
    method: "DELETE",
  });
}


export function activarUnidadMedida(id: number) {
  return request<UnidadMedida>(`/unidades-medida/${id}/activar`, { method: "PATCH" });
}
