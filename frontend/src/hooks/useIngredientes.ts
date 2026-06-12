import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createIngrediente,
  deleteIngrediente,
  getIngredientes,
  updateIngrediente,
  activarIngrediente,
} from "../services/ingredienteService";

export function useIngredientes(params?: { page?: number; size?: number; incluir_eliminados?: boolean }) {
  return useQuery({
    queryKey: ["ingredientes", params],
    queryFn: () => getIngredientes(params),
  });
}

export function useCrearIngrediente() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createIngrediente,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["ingredientes"] });
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
    },
  });
}

export function useActualizarIngrediente() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Parameters<typeof updateIngrediente>[1] }) =>
      updateIngrediente(id, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["ingredientes"] });
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
    },
  });
}

export function useEliminarIngrediente() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteIngrediente,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["ingredientes"] });
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
    },
  });
}


export function useActivarIngrediente() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: activarIngrediente,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["ingredientes"] });
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
    },
  });
}
