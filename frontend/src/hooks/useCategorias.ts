import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createCategoria,
  deleteCategoria,
  getCategorias,
  updateCategoria,
  activarCategoria,
} from "../services/categoriaService";

export function useCategorias(params?: { page?: number; size?: number; incluir_eliminadas?: boolean }) {
  return useQuery({
    queryKey: ["categorias", params],
    queryFn: () => getCategorias(params),
  });
}

export function useCrearCategoria() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createCategoria,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["categorias"] });
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
    },
  });
}

export function useActualizarCategoria() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Parameters<typeof updateCategoria>[1] }) =>
      updateCategoria(id, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["categorias"] });
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
    },
  });
}

export function useEliminarCategoria() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteCategoria,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["categorias"] });
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
    },
  });
}


export function useActivarCategoria() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: activarCategoria,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["categorias"] });
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
    },
  });
}
