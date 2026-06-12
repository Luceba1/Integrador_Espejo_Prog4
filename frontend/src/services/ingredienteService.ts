import { request } from "./api";
import type { Ingrediente, IngredientePayload } from "../types/ingrediente";

export function getIngredientes(params?: { page?: number; size?: number; incluir_eliminados?: boolean }) {
  const query = new URLSearchParams();
  if (params?.page) query.set("page", String(params.page));
  if (params?.size) query.set("size", String(params.size));
  if (typeof params?.incluir_eliminados === "boolean") query.set("incluir_eliminados", String(params.incluir_eliminados));
  const suffix = query.toString();
  return request<Ingrediente[]>(`/ingredientes/${suffix ? `?${suffix}` : ""}`);
}

export function createIngrediente(payload: IngredientePayload) {
  return request<Ingrediente>("/ingredientes/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateIngrediente(id: number, payload: IngredientePayload) {
  return request<Ingrediente>(`/ingredientes/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteIngrediente(id: number) {
  return request<void>(`/ingredientes/${id}`, {
    method: "DELETE",
  });
}

export function activarIngrediente(id: number) {
  return request<Ingrediente>(`/ingredientes/${id}/activar`, { method: "PATCH" });
}
