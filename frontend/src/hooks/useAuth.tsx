import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useQueryClient } from "@tanstack/react-query";

import * as authService from "../services/authService";
import type { AuthResponse, LoginPayload, Usuario } from "../types/auth";

interface AuthContextValue {
  usuario: Usuario | null;
  roles: string[];
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  logout: () => Promise<void>;
  refreshMe: () => Promise<void>;
  hasRole: (...allowedRoles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function normalizeAuth(response: AuthResponse) {
  return {
    usuario: response.usuario,
    roles: response.roles ?? response.usuario.roles.map((rol) => rol.codigo),
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [roles, setRoles] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const refreshMe = useCallback(async () => {
    const response = await authService.getMe();
    const auth = normalizeAuth(response);
    setUsuario(auth.usuario);
    setRoles(auth.roles);
  }, []);

  useEffect(() => {
    let mounted = true;

    authService
      .getMe()
      .then((response) => {
        if (!mounted) return;
        const auth = normalizeAuth(response);
        setUsuario(auth.usuario);
        setRoles(auth.roles);
      })
      .catch(() => {
        if (!mounted) return;
        setUsuario(null);
        setRoles([]);
      })
      .finally(() => {
        if (mounted) setIsLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    const response = await authService.login(payload);
    const auth = normalizeAuth(response);
    setUsuario(auth.usuario);
    setRoles(auth.roles);
    await queryClient.invalidateQueries();
  }, [queryClient]);

  const logout = useCallback(async () => {
    await authService.logout();
    setUsuario(null);
    setRoles([]);
    queryClient.clear();
  }, [queryClient]);

  const hasRole = useCallback(
    (...allowedRoles: string[]) => roles.some((rol) => allowedRoles.includes(rol)),
    [roles]
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      usuario,
      roles,
      isAuthenticated: Boolean(usuario),
      isLoading,
      login,
      logout,
      refreshMe,
      hasRole,
    }),
    [usuario, roles, isLoading, login, logout, refreshMe, hasRole]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth debe usarse dentro de AuthProvider.");
  }

  return context;
}
