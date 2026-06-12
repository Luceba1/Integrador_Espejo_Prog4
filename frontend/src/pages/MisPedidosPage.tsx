import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { useCancelarPedido, useEstadosPedido, usePedidos } from "../hooks/usePedidos";
import { usePedidoWebSocket } from "../hooks/usePedidoWebSocket";
import { confirmarPagoMercadoPago, crearPreferenciaPago } from "../services/pagoService";
import type { Pedido } from "../types/pedido";

const PAGE_SIZE = 10;

function formatMoney(value: number) {
  return new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" }).format(value);
}

function EstadoBadge({ estado }: { estado: string }) {
  const styles: Record<string, string> = {
    PENDIENTE: "bg-amber-500/15 text-amber-200",
    CONFIRMADO: "bg-sky-500/15 text-sky-200",
    EN_PREPARACION: "bg-purple-500/15 text-purple-200",
    ENTREGADO: "bg-emerald-500/15 text-emerald-200",
    CANCELADO: "bg-rose-500/15 text-rose-200",
  };

  return <span className={`rounded-full px-3 py-1 text-xs font-semibold ${styles[estado] ?? "bg-slate-500/15 text-slate-200"}`}>{estado}</span>;
}

function canCancel(pedido: Pedido) {
  return ["PENDIENTE", "CONFIRMADO"].includes(pedido.estado_codigo);
}

function canPayWithMercadoPago(pedido: Pedido) {
  return pedido.forma_pago_codigo === "MERCADOPAGO" && pedido.estado_codigo === "PENDIENTE";
}

function getPaymentIdFromParams(searchParams: URLSearchParams) {
  const raw = searchParams.get("payment_id") ?? searchParams.get("collection_id");
  const parsed = raw ? Number(raw) : NaN;
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
}

export default function MisPedidosPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const creado = searchParams.get("creado");
  const pedidoParam = searchParams.get("pedido");
  const mpStatus = searchParams.get("mp_status");
  const [estado, setEstado] = useState("");
  const [page, setPage] = useState(1);
  const [paymentMessage, setPaymentMessage] = useState<string | null>(null);
  const [payingPedidoId, setPayingPedidoId] = useState<number | null>(null);
  const pedidosQuery = usePedidos({ estado_codigo: estado || undefined, page, size: PAGE_SIZE });
  const estadosQuery = useEstadosPedido();
  const cancelarMutation = useCancelarPedido();
  const pedidoWs = usePedidoWebSocket({ mode: "mis-pedidos" });
  const canGoNext = useMemo(() => (pedidosQuery.data?.length ?? 0) === PAGE_SIZE, [pedidosQuery.data]);

  useEffect(() => {
    if (pedidoWs.eventCount > 0) {
      void pedidosQuery.refetch();
    }
  }, [pedidoWs.eventCount]);

  useEffect(() => {
    async function confirmarRetornoMercadoPago() {
      if (!pedidoParam || !mpStatus) return;

      const pedidoId = Number(pedidoParam);
      if (!Number.isFinite(pedidoId) || pedidoId <= 0) return;

      try {
        const paymentId = getPaymentIdFromParams(searchParams);
        const result = await confirmarPagoMercadoPago(pedidoId, paymentId);

        if (result.estado === "aprobado") {
          setPaymentMessage(`Pago aprobado. El pedido #${pedidoId} pasó a ${result.pedido_estado ?? "CONFIRMADO"}.`);
        } else if (result.estado === "rechazado") {
          setPaymentMessage(`El pago del pedido #${pedidoId} fue rechazado. Podés reintentar el pago.`);
        } else {
          setPaymentMessage(`El pago del pedido #${pedidoId} quedó ${result.estado ?? "pendiente"}.`);
        }

        await pedidosQuery.refetch();
      } catch (error) {
        setPaymentMessage(error instanceof Error ? error.message : "No se pudo confirmar el pago con MercadoPago.");
      } finally {
        const next = new URLSearchParams(searchParams);
        next.delete("mp_status");
        next.delete("collection_id");
        next.delete("collection_status");
        next.delete("payment_id");
        next.delete("status");
        next.delete("external_reference");
        next.delete("merchant_order_id");
        next.delete("preference_id");
        setSearchParams(next, { replace: true });
      }
    }

    void confirmarRetornoMercadoPago();
    // Se ejecuta una vez por retorno de MercadoPago. searchParams se limpia al finalizar.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pedidoParam, mpStatus]);

  async function cancelar(pedido: Pedido) {
    const ok = window.confirm(`¿Seguro que querés cancelar el pedido #${pedido.id}?`);
    if (!ok) return;

    try {
      await cancelarMutation.mutateAsync({ id: pedido.id, motivo: "Cancelado desde Store por el cliente" });
      window.alert(
        pedido.estado_codigo === "CONFIRMADO"
          ? "Pedido cancelado. El stock de ingredientes fue recuperado correctamente."
          : "Pedido cancelado correctamente."
      );
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo cancelar el pedido.");
    }
  }

  async function pagarConMercadoPago(pedido: Pedido) {
    setPayingPedidoId(pedido.id);
    try {
      const pago = await crearPreferenciaPago(pedido.id);
      const checkoutUrl = pago.init_point ?? pago.sandbox_init_point;
      if (!checkoutUrl) throw new Error("MercadoPago no devolvió un link de pago.");
      window.location.href = checkoutUrl;
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo iniciar MercadoPago.");
      setPayingPedidoId(null);
    }
  }

  return (
    <section className="space-y-6">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.25em] text-emerald-300">Pedidos</p>
        <h2 className="mt-2 text-3xl font-bold text-white">Mis pedidos</h2>
        <p className="mt-2 text-slate-400">El usuario CLIENT ve solamente sus propios pedidos.</p>
        <p className="mt-2 text-xs text-slate-500">WebSocket pedidos: {pedidoWs.status === "connected" ? "conectado" : pedidoWs.status}</p>
      </div>

      {creado ? (
        <div className="rounded-3xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-emerald-200">
          Pedido #{creado} creado correctamente.
        </div>
      ) : null}

      {paymentMessage ? (
        <div className="rounded-3xl border border-sky-500/30 bg-sky-500/10 p-4 text-sky-100">
          {paymentMessage}
        </div>
      ) : null}

      <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <select
          value={estado}
          onChange={(event) => {
            setEstado(event.target.value);
            setPage(1);
          }}
          className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none md:w-72"
        >
          <option value="">Todos los estados</option>
          {(estadosQuery.data ?? []).map((item) => <option key={item.codigo} value={item.codigo}>{item.codigo}</option>)}
        </select>
      </div>

      {pedidosQuery.isLoading ? <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-slate-300">Cargando pedidos...</div> : null}
      {pedidosQuery.isError ? (
        <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-rose-200">
          {pedidosQuery.error instanceof Error ? pedidosQuery.error.message : "No se pudieron cargar tus pedidos."}
        </div>
      ) : null}

      {pedidosQuery.data ? (
        <div className="space-y-4">
          {pedidosQuery.data.map((pedido) => (
            <article key={pedido.id} className="rounded-3xl border border-white/10 bg-slate-900/70 p-5">
              <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-3">
                    <h3 className="text-xl font-bold text-white">Pedido #{pedido.id}</h3>
                    <EstadoBadge estado={pedido.estado_codigo} />
                  </div>
                  <p className="mt-2 text-sm text-slate-400">Pago {pedido.forma_pago_codigo} · {new Date(pedido.created_at).toLocaleString("es-AR")}</p>
                  <p className="mt-2 text-lg font-semibold text-emerald-300">{formatMoney(Number(pedido.total))}</p>
                </div>
                <div className="flex flex-col gap-2 md:items-end">
                  {canPayWithMercadoPago(pedido) ? (
                    <button
                      type="button"
                      onClick={() => pagarConMercadoPago(pedido)}
                      disabled={payingPedidoId === pedido.id}
                      className="rounded-2xl border border-sky-500/30 px-4 py-3 text-sm font-semibold text-sky-200 hover:bg-sky-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {payingPedidoId === pedido.id ? "Abriendo MercadoPago..." : "Pagar con MercadoPago"}
                    </button>
                  ) : null}
                  <button
                    type="button"
                    onClick={() => cancelar(pedido)}
                    disabled={!canCancel(pedido) || cancelarMutation.isPending}
                    className="rounded-2xl border border-rose-500/30 px-4 py-3 text-sm font-semibold text-rose-200 hover:bg-rose-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {canCancel(pedido) ? "Cancelar pedido" : "No cancelable"}
                  </button>
                </div>
              </div>

              <div className="mt-5 grid gap-3 md:grid-cols-2">
                {pedido.detalles.map((detalle) => (
                  <div key={`${pedido.id}-${detalle.producto_id}-${detalle.created_at}`} className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                    <p className="font-semibold text-white">{detalle.nombre_producto_snap}</p>
                    <p className="mt-1 text-sm text-slate-400">Cantidad: {detalle.cantidad}</p>
                    <p className="mt-1 text-sm text-emerald-300">Subtotal: {formatMoney(Number(detalle.subtotal_snap))}</p>
                  </div>
                ))}
              </div>

              <details className="mt-4 rounded-2xl border border-white/10 bg-white/5 p-4">
                <summary className="cursor-pointer text-sm font-semibold text-slate-200">Ver historial de estados</summary>
                <div className="mt-3 space-y-2">
                  {pedido.historial_estados.map((historial) => (
                    <p key={historial.id} className="text-sm text-slate-400">
                      {historial.estado_desde ?? "Inicio"} → {historial.estado_hacia} · {new Date(historial.created_at).toLocaleString("es-AR")}
                    </p>
                  ))}
                </div>
              </details>
            </article>
          ))}
          {!pedidosQuery.data.length ? <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-center text-slate-400">Todavía no tenés pedidos.</div> : null}
        </div>
      ) : null}

      <div className="flex items-center justify-between rounded-3xl border border-white/10 bg-white/5 px-5 py-4">
        <button type="button" onClick={() => setPage((current) => Math.max(1, current - 1))} disabled={page === 1 || pedidosQuery.isFetching} className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10 disabled:opacity-50">
          Página anterior
        </button>
        <p className="text-sm text-slate-300">Página {page}</p>
        <button type="button" onClick={() => setPage((current) => current + 1)} disabled={!canGoNext || pedidosQuery.isFetching} className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10 disabled:opacity-50">
          Página siguiente
        </button>
      </div>
    </section>
  );
}
