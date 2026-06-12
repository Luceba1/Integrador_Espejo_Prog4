import { api } from "./api";
import type { AuthResponse, LoginPayload, RegisterPayload } from "../types/auth";

export async function login(payload: LoginPayload) {
  const response = await api.post<AuthResponse>("/auth/login", payload);
  return response.data;
}

export async function register(payload: RegisterPayload) {
  const response = await api.post<AuthResponse>("/auth/register", payload);
  return response.data;
}

export async function refreshSession() {
  const response = await api.post<AuthResponse>("/auth/refresh");
  return response.data;
}

export async function getMe() {
  const response = await api.get<AuthResponse>("/auth/me");
  return response.data;
}

export async function logout() {
  await api.post<void>("/auth/logout");
}
