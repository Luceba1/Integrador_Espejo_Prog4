import { api } from "./api";
import type { Rol } from "../types/auth";
import type {
  UsuarioAdmin,
  UsuarioAdminUpdatePayload,
  UsuarioRolesUpdatePayload,
} from "../types/admin";

export async function getRoles() {
  const response = await api.get<Rol[]>("/admin/roles");
  return response.data;
}

export async function getUsuarios(params: {
  rol?: string;
  search?: string;
  page?: number;
  size?: number;
  incluir_eliminados?: boolean;
}) {
  const response = await api.get<UsuarioAdmin[]>("/admin/usuarios", { params });
  return response.data;
}

export async function updateUsuario(id: number, payload: UsuarioAdminUpdatePayload) {
  const response = await api.put<UsuarioAdmin>(`/admin/usuarios/${id}`, payload);
  return response.data;
}

export async function updateUsuarioRoles(id: number, payload: UsuarioRolesUpdatePayload) {
  const response = await api.patch<UsuarioAdmin>(`/admin/usuarios/${id}/roles`, payload);
  return response.data;
}

export async function deleteUsuario(id: number) {
  await api.delete<void>(`/admin/usuarios/${id}`);
}


export async function activarUsuario(id: number) {
  const response = await api.patch<UsuarioAdmin>(`/admin/usuarios/${id}/activar`);
  return response.data;
}
