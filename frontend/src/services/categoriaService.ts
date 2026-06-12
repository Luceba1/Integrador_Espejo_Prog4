import { request } from "./api";
import type { Categoria, CategoriaPayload } from "../types/categoria";

export function getCategorias(params?: { page?: number; size?: number; incluir_eliminadas?: boolean }) {
  const query = new URLSearchParams();
  query.set("size", String(params?.size ?? 100));
  if (params?.page) query.set("page", String(params.page));
  if (typeof params?.incluir_eliminadas === "boolean") query.set("incluir_eliminadas", String(params.incluir_eliminadas));
  return request<Categoria[]>(`/categorias/?${query.toString()}`);
}

export function createCategoria(payload: CategoriaPayload) {
  return request<Categoria>("/categorias/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateCategoria(id: number, payload: CategoriaPayload) {
  return request<Categoria>(`/categorias/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteCategoria(id: number) {
  return request<void>(`/categorias/${id}`, {
    method: "DELETE",
  });
}

export function activarCategoria(id: number) {
  return request<Categoria>(`/categorias/${id}/activar`, { method: "PATCH" });
}
