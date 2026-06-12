import type { Rol } from "./auth";

export interface UsuarioAdmin {
  id: number;
  email: string;
  nombre: string;
  apellido?: string | null;
  activo: boolean;
  roles: Rol[];
  created_at: string;
  updated_at: string;
  deleted_at?: string | null;
}

export interface UsuarioAdminUpdatePayload {
  email?: string;
  nombre?: string;
  apellido?: string | null;
  activo?: boolean;
}

export interface UsuarioRolesUpdatePayload {
  roles: string[];
}
