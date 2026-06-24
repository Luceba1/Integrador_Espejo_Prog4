import { useMutation, useQuery, useQueryClient, type QueryClient } from "@tanstack/react-query";

import {
  avanzarEstadoPedido,
  cancelarPedido,
  getEstadosPedido,
  getFormasPago,
  getPedidos,
  createPedido,
} from "../services/pedidoService";

async function invalidatePedidoYStockQueries(queryClient: QueryClient) {
  await Promise.all([
    queryClient.invalidateQueries({ queryKey: ["pedidos"] }),
    queryClient.invalidateQueries({ queryKey: ["productos"] }),
    queryClient.invalidateQueries({ queryKey: ["producto"] }),
    queryClient.invalidateQueries({ queryKey: ["ingredientes"] }),
    queryClient.invalidateQueries({ queryKey: ["admin", "dashboard"] }),
  ]);
}

export function usePedidos(filters: { estado_codigo?: string; usuario_id?: number; page: number; size: number }) {
  return useQuery({
    queryKey: ["pedidos", filters],
    queryFn: () => getPedidos(filters),
  });
}

export function useEstadosPedido() {
  return useQuery({
    queryKey: ["pedidos", "estados"],
    queryFn: getEstadosPedido,
  });
}

export function useFormasPago() {
  return useQuery({
    queryKey: ["pedidos", "formas-pago"],
    queryFn: getFormasPago,
  });
}

export function useAvanzarEstadoPedido() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, estado_codigo, motivo, recuperar_stock }: { id: number; estado_codigo: string; motivo?: string; recuperar_stock?: boolean }) =>
      avanzarEstadoPedido(id, { estado_codigo, motivo, recuperar_stock }),
    onSuccess: async () => {
      await invalidatePedidoYStockQueries(queryClient);
    },
  });
}

export function useCancelarPedido() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, motivo }: { id: number; motivo?: string }) => cancelarPedido(id, motivo),
    onSuccess: async () => {
      await invalidatePedidoYStockQueries(queryClient);
    },
  });
}

export function useCrearPedido() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createPedido,
    onSuccess: async () => {
      await invalidatePedidoYStockQueries(queryClient);
    },
  });
}
