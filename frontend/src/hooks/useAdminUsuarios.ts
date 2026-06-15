import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  deleteUsuario,
  getDashboardMetricas,
  getRoles,
  getUsuarios,
  updateUsuario,
  updateUsuarioRoles,
  activarUsuario,
} from "../services/adminService";

export function useDashboardMetricas() {
  return useQuery({
    queryKey: ["admin", "dashboard"],
    queryFn: getDashboardMetricas,
  });
}

export function useRoles() {
  return useQuery({
    queryKey: ["admin", "roles"],
    queryFn: getRoles,
  });
}

export function useUsuariosAdmin(filters: { rol?: string; search?: string; page: number; size: number; incluir_eliminados?: boolean }) {
  return useQuery({
    queryKey: ["admin", "usuarios", filters],
    queryFn: () => getUsuarios(filters),
  });
}

export function useActualizarUsuario() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Parameters<typeof updateUsuario>[1] }) =>
      updateUsuario(id, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin", "usuarios"] });
    },
  });
}

export function useActualizarRolesUsuario() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, roles }: { id: number; roles: string[] }) => updateUsuarioRoles(id, { roles }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin", "usuarios"] });
    },
  });
}

export function useEliminarUsuario() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteUsuario,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin", "usuarios"] });
    },
  });
}


export function useActivarUsuario() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: activarUsuario,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin", "usuarios"] });
    },
  });
}
