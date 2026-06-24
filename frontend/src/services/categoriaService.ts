import { request } from "./api";
import type { Categoria, CategoriaPayload } from "../types/categoria";

export interface CategoriaQueryParams {
  page?: number;
  size?: number;
  incluir_eliminadas?: boolean;
  solo_raiz?: boolean;
  search?: string;
  full?: boolean;
}

function buildCategoriaQuery(params?: CategoriaQueryParams, pageOverride?: number, sizeOverride?: number) {
  const query = new URLSearchParams();
  query.set("size", String(sizeOverride ?? params?.size ?? 100));
  if (pageOverride ?? params?.page) query.set("page", String(pageOverride ?? params?.page));
  if (typeof params?.incluir_eliminadas === "boolean") {
    query.set("incluir_eliminadas", String(params.incluir_eliminadas));
  }
  if (typeof params?.solo_raiz === "boolean") {
    query.set("solo_raiz", String(params.solo_raiz));
  }
  if (params?.search?.trim()) {
    query.set("search", params.search.trim());
  }
  return query;
}

export async function getCategorias(params?: CategoriaQueryParams) {
  if (!params?.full) {
    return request<Categoria[]>(`/categorias/?${buildCategoriaQuery(params).toString()}`);
  }

  const all: Categoria[] = [];
  const size = 100;
  let page = 1;

  while (true) {
    const query = buildCategoriaQuery(params, page, size);
    const pageItems = await request<Categoria[]>(`/categorias/?${query.toString()}`);
    all.push(...pageItems);

    if (pageItems.length < size) break;
    page += 1;
  }

  return all;
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
