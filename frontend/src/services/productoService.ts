import { request } from "./api";
import type { Producto, ProductoDisponibilidadPayload, ProductoPayload, ProductoStockPayload } from "../types/producto";

export function getProductos(search = "", page = 1, size = 10, filters?: { disponible?: boolean; incluir_eliminados?: boolean }) {
  const params = new URLSearchParams();

  if (search.trim()) params.set("search", search.trim());
  if (typeof filters?.disponible === "boolean") params.set("disponible", String(filters.disponible));
  if (typeof filters?.incluir_eliminados === "boolean") params.set("incluir_eliminados", String(filters.incluir_eliminados));
  params.set("page", String(page));
  params.set("size", String(size));

  return request<Producto[]>(`/productos/?${params.toString()}`);
}

export function getProductoById(id: number) {
  return request<Producto>(`/productos/${id}`);
}

export function createProducto(payload: ProductoPayload) {
  return request<Producto>("/productos/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateProducto(id: number, payload: ProductoPayload) {
  return request<Producto>(`/productos/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function cambiarDisponibilidadProducto(id: number, payload: ProductoDisponibilidadPayload) {
  return request<Producto>(`/productos/${id}/disponibilidad`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function actualizarStockProducto(id: number, payload: ProductoStockPayload) {
  return request<Producto>(`/productos/${id}/stock`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}


export function deleteProducto(id: number) {
  return request<void>(`/productos/${id}`, {
    method: "DELETE",
  });
}


export function activarProducto(id: number) {
  return request<Producto>(`/productos/${id}/activar`, {
    method: "PATCH",
  });
}
