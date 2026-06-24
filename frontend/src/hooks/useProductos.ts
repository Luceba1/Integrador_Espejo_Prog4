import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createProducto,
  actualizarStockProducto,
  cambiarDisponibilidadProducto,
  deleteProducto,
  getProductoById,
  getProductos,
  updateProducto,
  activarProducto,
} from "../services/productoService";

export function useProductos(search: string, page: number, size: number, filters?: { disponible?: boolean; incluir_eliminados?: boolean; categoria_id?: number }) {
  return useQuery({
    queryKey: ["productos", search, page, size, filters],
    queryFn: () => getProductos(search, page, size, filters),
    refetchInterval: filters?.disponible === true ? 15000 : false,
    refetchIntervalInBackground: false,
  });
}

export function useProducto(id: number) {
  return useQuery({
    queryKey: ["producto", id],
    queryFn: () => getProductoById(id),
    enabled: Number.isInteger(id) && id > 0,
    refetchInterval: 15000,
    refetchIntervalInBackground: false,
  });
}

export function useCrearProducto() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createProducto,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
    },
  });
}

export function useActualizarProducto() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Parameters<typeof updateProducto>[1] }) =>
      updateProducto(id, payload),
    onSuccess: async (_, variables) => {
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
      await queryClient.invalidateQueries({ queryKey: ["producto", variables.id] });
    },
  });
}

export function useEliminarProducto() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteProducto,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
    },
  });
}


export function useCambiarDisponibilidadProducto() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, disponible }: { id: number; disponible: boolean }) =>
      cambiarDisponibilidadProducto(id, { disponible }),
    onSuccess: async (_, variables) => {
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
      await queryClient.invalidateQueries({ queryKey: ["producto", variables.id] });
    },
  });
}


export function useActualizarStockProducto() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, stock_cantidad }: { id: number; stock_cantidad: number }) =>
      actualizarStockProducto(id, { stock_cantidad }),
    onSuccess: async (_, variables) => {
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
      await queryClient.invalidateQueries({ queryKey: ["producto", variables.id] });
    },
  });
}


export function useActivarProducto() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: activarProducto,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["productos"] });
    },
  });
}
