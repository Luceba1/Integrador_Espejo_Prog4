import { useEffect, useMemo, useState } from "react";

import PageContainer from "../components/layout/PageContainer";
import {
  useAvanzarEstadoPedido,
  useEstadosPedido,
  usePedidos,
} from "../hooks/usePedidos";
import { usePedidoWebSocket } from "../hooks/usePedidoWebSocket";
import type { Pedido } from "../types/pedido";

const PAGE_SIZE = 10;

const siguienteEstado: Record<string, string> = {
  PENDIENTE: "CONFIRMADO",
  CONFIRMADO: "EN_PREP",
  EN_PREP: "ENTREGADO",
};

function formatMoney(value: number) {
  return new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" }).format(value);
}

function EstadoBadge({ estado }: { estado: string }) {
  return (
    <span className="rounded-full bg-sky-500/15 px-3 py-1 text-xs font-semibold text-sky-200">
      {estado}
    </span>
  );
}

export default function CajeroPedidosPage() {
  const [estado, setEstado] = useState("");
  const [page, setPage] = useState(1);
  const pedidosQuery = usePedidos({ estado_codigo: estado || undefined, page, size: PAGE_SIZE });
  const estadosQuery = useEstadosPedido();
  const avanzarMutation = useAvanzarEstadoPedido();
  const pedidoWs = usePedidoWebSocket({ mode: "admin" });

  const canGoNext = useMemo(() => (pedidosQuery.data?.length ?? 0) === PAGE_SIZE, [pedidosQuery.data]);

  useEffect(() => {
    if (pedidoWs.eventCount > 0) {
      void pedidosQuery.refetch();
    }
  }, [pedidoWs.eventCount]);

  async function avanzar(pedido: Pedido) {
    const next = siguienteEstado[pedido.estado_codigo];
    if (!next) return;

    try {
      await avanzarMutation.mutateAsync({
        id: pedido.id,
        estado_codigo: next,
        motivo: `Avance desde panel de pedidos: ${pedido.estado_codigo} -> ${next}`,
      });
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo avanzar el estado.");
    }
  }

  async function cancelarPedido(pedido: Pedido) {
    const ok = window.confirm(`¿Seguro que querés cancelar el pedido #${pedido.id}?`);
    if (!ok) return;

    const puedeHaberConsumidoStock = ["CONFIRMADO", "EN_PREP"].includes(pedido.estado_codigo);
    const recuperarStock = puedeHaberConsumidoStock
      ? window.confirm(
          "¿Querés recuperar los ingredientes al stock?\n\n" +
            "Aceptá si los ingredientes todavía no fueron usados.\n" +
            "Cancelá si el pedido ya estaba en preparación y los ingredientes ya se consumieron."
        )
      : false;

    try {
      await avanzarMutation.mutateAsync({
        id: pedido.id,
        estado_codigo: "CANCELADO",
        motivo: `Cancelado desde panel de pedidos. Estado anterior: ${pedido.estado_codigo}. Recupera stock: ${recuperarStock ? "sí" : "no"}`,
        recuperar_stock: recuperarStock,
      });
      window.alert(
        recuperarStock
          ? "Pedido cancelado. El stock de ingredientes fue recuperado correctamente."
          : "Pedido cancelado sin recuperar ingredientes al stock."
      );
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo cancelar el pedido.");
    }
  }

  return (
    <PageContainer
      title="Pedidos / Cajero"
      subtitle={`Pantalla para rol ADMIN o PEDIDOS. Actualización en tiempo real por WebSocket: ${pedidoWs.status === "connected" ? "conectado" : pedidoWs.status}.`}
    >
      <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <div className="grid gap-3 md:grid-cols-[260px_auto]">
          <select
            value={estado}
            onChange={(event) => {
              setEstado(event.target.value);
              setPage(1);
            }}
            className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
          >
            <option value="">Todos los estados</option>
            {(estadosQuery.data ?? []).map((item) => (
              <option key={item.codigo} value={item.codigo}>{item.codigo}</option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => pedidosQuery.refetch()}
            className="rounded-2xl border border-white/10 px-4 py-3 font-semibold text-slate-100 hover:bg-white/10"
          >
            Actualizar listado
          </button>
        </div>
      </div>

      {pedidosQuery.isLoading ? (
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-slate-300">Cargando pedidos...</div>
      ) : null}

      {pedidosQuery.isError ? (
        <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-rose-200">
          {pedidosQuery.error instanceof Error ? pedidosQuery.error.message : "No se pudieron cargar los pedidos."}
        </div>
      ) : null}

      {pedidosQuery.data ? (
        <div className="space-y-4">
          {pedidosQuery.data.map((pedido) => {
            const next = siguienteEstado[pedido.estado_codigo];
            return (
              <article key={pedido.id} className="rounded-3xl border border-white/10 bg-slate-900/70 p-5">
                <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                  <div>
                    <div className="flex flex-wrap items-center gap-3">
                      <h3 className="text-xl font-bold text-white">Pedido #{pedido.id}</h3>
                      <EstadoBadge estado={pedido.estado_codigo} />
                    </div>
                    <p className="mt-2 text-sm text-slate-400">Usuario #{pedido.usuario_id} · Pago {pedido.forma_pago_codigo}</p>
                    <div className="mt-3 flex flex-wrap gap-2 text-xs font-semibold">
                      <span className={pedido.tipo_entrega === "ENVIO" ? "rounded-full bg-sky-500/15 px-3 py-1 text-sky-200" : "rounded-full bg-emerald-500/15 px-3 py-1 text-emerald-200"}>
                        {pedido.tipo_entrega === "ENVIO" ? "Envío a domicilio" : "Retiro en el lugar"}
                      </span>
                    </div>
                    {pedido.tipo_entrega === "RETIRO" && pedido.domicilio_retiro_snap ? (
                      <p className="mt-2 text-sm text-slate-400">Retiro: {pedido.domicilio_retiro_snap}</p>
                    ) : null}
                    {pedido.forma_pago_codigo === "TRANSFERENCIA" && pedido.datos_transferencia_snap ? (
                      <p className="mt-2 text-sm text-sky-200">Transferencia: {pedido.datos_transferencia_snap}</p>
                    ) : null}
                    <p className="mt-2 text-lg font-semibold text-emerald-300">{formatMoney(pedido.total)}</p>
                  </div>
                  <div className="flex flex-col gap-2 md:items-end">
                    <button
                      type="button"
                      onClick={() => avanzar(pedido)}
                      disabled={!next || avanzarMutation.isPending}
                      className="rounded-2xl bg-blue-500 px-4 py-3 font-semibold text-white hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {next ? `Avanzar a ${next}` : "Estado final"}
                    </button>
                    {!["ENTREGADO", "CANCELADO"].includes(pedido.estado_codigo) ? (
                      <button
                        type="button"
                        onClick={() => cancelarPedido(pedido)}
                        disabled={avanzarMutation.isPending}
                        className="rounded-2xl border border-rose-500/30 px-4 py-3 text-sm font-semibold text-rose-200 hover:bg-rose-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        Cancelar pedido
                      </button>
                    ) : null}
                  </div>
                </div>

                <div className="mt-5 grid gap-3 md:grid-cols-2">
                  {pedido.detalles.map((detalle) => (
                    <div key={`${pedido.id}-${detalle.producto_id}-${detalle.created_at}`} className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                      <p className="font-semibold text-white">{detalle.nombre_producto_snap}</p>
                      <p className="mt-1 text-sm text-slate-400">Cantidad: {detalle.cantidad}</p>
                      <p className="mt-1 text-sm text-emerald-300">Subtotal: {formatMoney(detalle.subtotal_snap)}</p>
                    </div>
                  ))}
                </div>
              </article>
            );
          })}
          {!pedidosQuery.data.length ? (
            <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-center text-slate-400">
              No hay pedidos para mostrar.
            </div>
          ) : null}
        </div>
      ) : null}

      <div className="flex items-center justify-between rounded-3xl border border-white/10 bg-white/5 px-5 py-4">
        <button
          type="button"
          onClick={() => setPage((current) => Math.max(1, current - 1))}
          disabled={page === 1 || pedidosQuery.isFetching}
          className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10 disabled:opacity-50"
        >
          Página anterior
        </button>
        <p className="text-sm text-slate-300">Página {page}</p>
        <button
          type="button"
          onClick={() => setPage((current) => current + 1)}
          disabled={!canGoNext || pedidosQuery.isFetching}
          className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10 disabled:opacity-50"
        >
          Página siguiente
        </button>
      </div>
    </PageContainer>
  );
}
