export type RolCodigo = "ADMIN" | "STOCK" | "PEDIDOS" | "CLIENT";

export interface Rol {
  id: number;
  codigo: RolCodigo | string;
  nombre: string;
}

export interface Usuario {
  id: number;
  email: string;
  nombre: string;
  apellido?: string | null;
  roles: Rol[];
  created_at: string;
}

export interface AuthResponse {
  usuario: Usuario;
  roles: string[];
  access_token?: string | null;
  refresh_token?: string | null;
  token_type?: string;
  expires_in?: number | null;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  nombre: string;
  apellido?: string | null;
  password: string;
}
