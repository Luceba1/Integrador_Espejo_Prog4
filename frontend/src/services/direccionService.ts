import { api } from "./api";
import type { DireccionEntrega, DireccionPayload } from "../types/direccion";

export async function getDirecciones() {
  const response = await api.get<DireccionEntrega[]>("/direcciones/");
  return response.data;
}

export async function createDireccion(payload: DireccionPayload) {
  const response = await api.post<DireccionEntrega>("/direcciones/", payload);
  return response.data;
}

export async function updateDireccion(id: number, payload: Partial<DireccionPayload>) {
  const response = await api.put<DireccionEntrega>(`/direcciones/${id}`, payload);
  return response.data;
}

export async function marcarDireccionPrincipal(id: number) {
  const response = await api.patch<DireccionEntrega>(`/direcciones/${id}/principal`);
  return response.data;
}

export async function deleteDireccion(id: number) {
  await api.delete<void>(`/direcciones/${id}`);
}
