import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createDireccion,
  deleteDireccion,
  getDirecciones,
  marcarDireccionPrincipal,
  updateDireccion,
} from "../services/direccionService";
import type { DireccionPayload } from "../types/direccion";

export function useDirecciones() {
  return useQuery({
    queryKey: ["direcciones"],
    queryFn: getDirecciones,
  });
}

export function useCrearDireccion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createDireccion,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["direcciones"] });
    },
  });
}

export function useActualizarDireccion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<DireccionPayload> }) => updateDireccion(id, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["direcciones"] });
    },
  });
}

export function useMarcarDireccionPrincipal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: marcarDireccionPrincipal,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["direcciones"] });
    },
  });
}

export function useEliminarDireccion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteDireccion,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["direcciones"] });
    },
  });
}
