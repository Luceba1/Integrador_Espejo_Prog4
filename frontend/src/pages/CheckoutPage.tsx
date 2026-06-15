import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import CartSummary from "../components/store/CartSummary";
import { useCarrito } from "../hooks/useCarrito";
import { useCrearDireccion, useDirecciones } from "../hooks/useDirecciones";
import { useCrearPedido, useFormasPago } from "../hooks/usePedidos";
import { crearPreferenciaPago } from "../services/pagoService";
import { usePagoStore } from "../stores/pagoStore";
import type { DireccionPayload } from "../types/direccion";

const COSTO_ENVIO_DEMO = 500;

export default function CheckoutPage() {
  const navigate = useNavigate();
  const { clearCart, hasItems, items, subtotal } = useCarrito();
  const direccionesQuery = useDirecciones();
  const formasPagoQuery = useFormasPago();
  const crearDireccionMutation = useCrearDireccion();
  const crearPedidoMutation = useCrearPedido();
  const setPagoPendiente = usePagoStore((state) => state.setPagoPendiente);
  const setEstadoPago = usePagoStore((state) => state.setEstadoPago);

  const [direccionId, setDireccionId] = useState<number | "">("");
  const [formaPagoCodigo, setFormaPagoCodigo] = useState("EFECTIVO");
  const [notas, setNotas] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [direccionForm, setDireccionForm] = useState<DireccionPayload>({
    etiqueta: "Casa",
    linea1: "",
    linea2: "",
    ciudad: "Mendoza",
    latitud: null,
    longitud: null,
    es_principal: false,
  });

  const direcciones = direccionesQuery.data ?? [];
  const selectedDireccionId = useMemo(() => {
    if (direccionId !== "") return direccionId;
    return direcciones.find((direccion) => direccion.es_principal)?.id ?? direcciones[0]?.id ?? "";
  }, [direccionId, direcciones]);

  async function crearDireccionRapida(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    try {
      const nueva = await crearDireccionMutation.mutateAsync(direccionForm);
      setDireccionId(nueva.id);
      setDireccionForm({ etiqueta: "Casa", linea1: "", linea2: "", ciudad: "Mendoza", latitud: null, longitud: null, es_principal: false });
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "No se pudo crear la dirección.");
    }
  }

  async function confirmarPedido() {
    if (!hasItems) return;
    if (!selectedDireccionId) {
      setFormError("Necesitás seleccionar o crear una dirección de entrega.");
      return;
    }
    if (!formaPagoCodigo) {
      setFormError("Seleccioná una forma de pago.");
      return;
    }

    setFormError(null);
    try {
      const pedido = await crearPedidoMutation.mutateAsync({
        direccion_id: Number(selectedDireccionId),
        forma_pago_codigo: formaPagoCodigo,
        notas: notas.trim() || null,
        descuento: 0,
        costo_envio: COSTO_ENVIO_DEMO,
        items: items.map((item) => ({ producto_id: item.producto_id, cantidad: item.cantidad, personalizacion: null })),
      });

      if (formaPagoCodigo === "MERCADOPAGO") {
        setPagoPendiente(pedido.id);
        const pago = await crearPreferenciaPago(pedido.id);
        const checkoutUrl = pago.init_point ?? pago.sandbox_init_point;
        if (checkoutUrl) {
          setEstadoPago("redirecting", "Redirigiendo a MercadoPago Checkout Pro.");
          clearCart();
          window.location.href = checkoutUrl;
          return;
        }
        setEstadoPago("error", "MercadoPago no devolvió un link de pago.");
        throw new Error("MercadoPago creó la preferencia, pero no devolvió un link de pago.");
      }

      clearCart();
      navigate(`/store/pedidos?creado=${pedido.id}`);
    } catch (error) {
      setEstadoPago("error", error instanceof Error ? error.message : "No se pudo realizar el pedido.");
      setFormError(error instanceof Error ? error.message : "No se pudo realizar el pedido.");
    }
  }

  if (!hasItems) {
    return (
      <section className="rounded-3xl border border-white/10 bg-white/5 p-8 text-center">
        <h2 className="text-2xl font-bold text-white">No hay productos para pedir.</h2>
        <Link to="/store" className="mt-4 inline-block rounded-2xl bg-emerald-500 px-5 py-3 font-semibold text-white hover:bg-emerald-400">
          Volver al catálogo
        </Link>
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.25em] text-emerald-300">Checkout</p>
        <h2 className="mt-2 text-3xl font-bold text-white">Realizar pedido</h2>
        <p className="mt-2 text-slate-400">El pedido se crea en estado PENDIENTE. Si elegís MercadoPago, se abre Checkout Pro y el stock se descuenta recién cuando el pago queda aprobado.</p>
      </div>

      {formError ? <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-4 text-rose-200">{formError}</div> : null}

      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="space-y-5">
          <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-5">
            <h3 className="text-xl font-bold text-white">Dirección de entrega</h3>
            {direccionesQuery.isLoading ? <p className="mt-3 text-slate-400">Cargando direcciones...</p> : null}
            <div className="mt-4 grid gap-3">
              {direcciones.map((direccion) => (
                <label key={direccion.id} className="flex cursor-pointer items-start gap-3 rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                  <input
                    type="radio"
                    name="direccion"
                    checked={Number(selectedDireccionId) === direccion.id}
                    onChange={() => setDireccionId(direccion.id)}
                    className="mt-1"
                  />
                  <span>
                    <span className="font-semibold text-white">{direccion.etiqueta ?? "Dirección"} {direccion.es_principal ? "· Principal" : ""}</span>
                    <span className="mt-1 block text-sm text-slate-400">{direccion.linea1}{direccion.linea2 ? `, ${direccion.linea2}` : ""} · {direccion.ciudad}</span>
                  </span>
                </label>
              ))}
            </div>

            <form className="mt-5 rounded-2xl border border-white/10 bg-white/5 p-4" onSubmit={crearDireccionRapida}>
              <h4 className="font-bold text-white">Crear dirección rápida</h4>
              <div className="mt-3 grid gap-3 md:grid-cols-2">
                <input value={direccionForm.etiqueta ?? ""} onChange={(e) => setDireccionForm((f) => ({ ...f, etiqueta: e.target.value }))} placeholder="Alias: Casa, Trabajo" className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none" />
                <input value={direccionForm.ciudad} onChange={(e) => setDireccionForm((f) => ({ ...f, ciudad: e.target.value }))} placeholder="Ciudad" className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none" />
                <input value={direccionForm.linea1} onChange={(e) => setDireccionForm((f) => ({ ...f, linea1: e.target.value }))} placeholder="Dirección principal" className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none md:col-span-2" />
                <input value={direccionForm.linea2 ?? ""} onChange={(e) => setDireccionForm((f) => ({ ...f, linea2: e.target.value }))} placeholder="Piso, dpto, referencia" className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none md:col-span-2" />
              </div>
              <button type="submit" disabled={crearDireccionMutation.isPending} className="mt-3 rounded-2xl border border-white/10 px-4 py-3 font-semibold text-slate-100 hover:bg-white/10 disabled:opacity-50">
                Guardar dirección
              </button>
            </form>
          </div>

          <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-5">
            <h3 className="text-xl font-bold text-white">Forma de pago y notas</h3>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <select value={formaPagoCodigo} onChange={(e) => setFormaPagoCodigo(e.target.value)} className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none">
                {(formasPagoQuery.data ?? []).map((forma) => <option key={forma.codigo} value={forma.codigo}>{forma.nombre}</option>)}
              </select>
              <input value={notas} onChange={(e) => setNotas(e.target.value)} placeholder="Notas para el pedido" className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none" />
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <CartSummary />
          <button type="button" onClick={confirmarPedido} disabled={crearPedidoMutation.isPending} className="w-full rounded-2xl bg-emerald-500 px-4 py-3 font-semibold text-white hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-50">
            {crearPedidoMutation.isPending ? "Creando pedido..." : `Crear pedido por $${(subtotal + COSTO_ENVIO_DEMO).toFixed(2)}`}
          </button>
        </div>
      </div>
    </section>
  );
}
