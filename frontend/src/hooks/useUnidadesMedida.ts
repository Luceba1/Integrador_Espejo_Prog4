import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createUnidadMedida,
  deleteUnidadMedida,
  getUnidadesMedida,
  type UnidadMedidaQueryParams,
  updateUnidadMedida,
  activarUnidadMedida,
} from "../services/unidadMedidaService";

export function useUnidadesMedida(params?: UnidadMedidaQueryParams) {
  return useQuery({
    queryKey: ["unidades-medida", params],
    queryFn: () => getUnidadesMedida(params),
  });
}

export function useCrearUnidadMedida() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createUnidadMedida,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["unidades-medida"] });
    },
  });
}

export function useActualizarUnidadMedida() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Parameters<typeof updateUnidadMedida>[1] }) =>
      updateUnidadMedida(id, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["unidades-medida"] });
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
    },
  });
}

export function useEliminarUnidadMedida() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteUnidadMedida,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["unidades-medida"] });
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
    },
  });
}


export function useActivarUnidadMedida() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: activarUnidadMedida,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["unidades-medida"] });
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
    },
  });
}
