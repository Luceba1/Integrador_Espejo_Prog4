import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import CartSummary from "../components/store/CartSummary";
import { useCarrito } from "../hooks/useCarrito";
import { useCrearDireccion, useDirecciones } from "../hooks/useDirecciones";
import { useConfiguracionEmpresa } from "../hooks/useEmpresa";
import { useCrearPedido, useFormasPago } from "../hooks/usePedidos";
import { crearPreferenciaPago } from "../services/pagoService";
import { usePagoStore } from "../stores/pagoStore";
import type { DireccionPayload } from "../types/direccion";

const COSTO_ENVIO_DOMICILIO = 500;
type TipoEntrega = "RETIRO" | "ENVIO";

function formatMoney(value: number) {
  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "ARS",
  }).format(value);
}

export default function CheckoutPage() {
  const navigate = useNavigate();
  const { clearCart, hasItems, items, subtotal } = useCarrito();
  const direccionesQuery = useDirecciones();
  const formasPagoQuery = useFormasPago();
  const empresaQuery = useConfiguracionEmpresa();
  const crearDireccionMutation = useCrearDireccion();
  const crearPedidoMutation = useCrearPedido();
  const setPagoPendiente = usePagoStore((state) => state.setPagoPendiente);
  const setEstadoPago = usePagoStore((state) => state.setEstadoPago);

  const [tipoEntrega, setTipoEntrega] = useState<TipoEntrega>("RETIRO");
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
  const formasPagoDisponibles = useMemo(() => {
    const formas = formasPagoQuery.data ?? [];
    if (tipoEntrega === "ENVIO") {
      return formas.filter((forma) => forma.codigo !== "EFECTIVO");
    }
    return formas;
  }, [formasPagoQuery.data, tipoEntrega]);

  const selectedDireccionId = useMemo(() => {
    if (direccionId !== "") return direccionId;
    return (
      direcciones.find((direccion) => direccion.es_principal)?.id ??
      direcciones[0]?.id ??
      ""
    );
  }, [direccionId, direcciones]);

  const costoEnvio = tipoEntrega === "ENVIO" ? COSTO_ENVIO_DOMICILIO : 0;
  const totalPedido = subtotal + costoEnvio;
  const empresaConfig = empresaQuery.data;
  const domicilioRetiro = empresaConfig?.domicilio_retiro?.trim();
  const mostrarDatosTransferencia = formaPagoCodigo === "TRANSFERENCIA";

  useEffect(() => {
    if (!formasPagoDisponibles.length) return;
    const actualPermitida = formasPagoDisponibles.some(
      (forma) => forma.codigo === formaPagoCodigo,
    );
    if (!actualPermitida) {
      setFormaPagoCodigo(formasPagoDisponibles[0].codigo);
    }
  }, [formaPagoCodigo, formasPagoDisponibles]);

  async function crearDireccionRapida(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    try {
      const nueva = await crearDireccionMutation.mutateAsync(direccionForm);
      setDireccionId(nueva.id);
      setDireccionForm({
        etiqueta: "Casa",
        linea1: "",
        linea2: "",
        ciudad: "Mendoza",
        latitud: null,
        longitud: null,
        es_principal: false,
      });
    } catch (error) {
      setFormError(
        error instanceof Error
          ? error.message
          : "No se pudo crear la dirección.",
      );
    }
  }

  async function confirmarPedido() {
    if (!hasItems) return;
    if (tipoEntrega === "ENVIO" && !selectedDireccionId) {
      setFormError(
        "Para envío a domicilio necesitás seleccionar o crear una dirección de entrega.",
      );
      return;
    }
    if (!formaPagoCodigo) {
      setFormError("Seleccioná una forma de pago.");
      return;
    }
    if (tipoEntrega === "ENVIO" && formaPagoCodigo === "EFECTIVO") {
      setFormError(
        "Para envío a domicilio solo se permite Transferencia o MercadoPago.",
      );
      return;
    }

    const notaTipoEntrega =
      tipoEntrega === "ENVIO"
        ? "Tipo de entrega: envío a domicilio."
        : "Tipo de entrega: retiro en el lugar.";
    const notasFinales = [notaTipoEntrega, notas.trim()]
      .filter(Boolean)
      .join(" ");

    setFormError(null);
    try {
      const pedido = await crearPedidoMutation.mutateAsync({
        direccion_id:
          tipoEntrega === "ENVIO" ? Number(selectedDireccionId) : null,
        tipo_entrega: tipoEntrega,
        forma_pago_codigo: formaPagoCodigo,
        notas: notasFinales || null,
        descuento: 0,
        costo_envio: costoEnvio,
        items: items.map((item) => ({
          producto_id: item.producto_id,
          cantidad: item.cantidad,
          personalizacion: null,
        })),
      });

      if (formaPagoCodigo === "MERCADOPAGO") {
        setPagoPendiente(pedido.id);
        const pago = await crearPreferenciaPago(pedido.id);
        const checkoutUrl = pago.init_point ?? pago.sandbox_init_point;
        if (checkoutUrl) {
          setEstadoPago(
            "redirecting",
            "Redirigiendo a MercadoPago Checkout Pro.",
          );
          clearCart();
          window.location.href = checkoutUrl;
          return;
        }
        setEstadoPago("error", "MercadoPago no devolvió un link de pago.");
        throw new Error(
          "MercadoPago creó la preferencia, pero no devolvió un link de pago.",
        );
      }

      clearCart();
      navigate(`/store/pedidos?creado=${pedido.id}`);
    } catch (error) {
      setEstadoPago(
        "error",
        error instanceof Error
          ? error.message
          : "No se pudo realizar el pedido.",
      );
      setFormError(
        error instanceof Error
          ? error.message
          : "No se pudo realizar el pedido.",
      );
    }
  }

  if (!hasItems) {
    return (
      <section className="rounded-3xl border border-white/10 bg-white/5 p-8 text-center">
        <h2 className="text-2xl font-bold text-white">
          No hay productos para pedir.
        </h2>
        <Link
          to="/store"
          className="mt-4 inline-block rounded-2xl bg-emerald-500 px-5 py-3 font-semibold text-white hover:bg-emerald-400"
        >
          Volver al catálogo
        </Link>
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <div>
        <Link
          to="/store/carrito"
          className="inline-flex items-center gap-2 rounded-2xl border border-emerald-400/30 bg-emerald-500/15 px-4 py-2 text-sm font-bold text-emerald-100 shadow-lg shadow-emerald-950/30 transition hover:bg-emerald-500/25 hover:text-white"
        >
          ← Volver
        </Link>
        <p className="mt-4 text-sm font-semibold uppercase tracking-[0.25em] text-emerald-300">
          Checkout
        </p>
        <h2 className="mt-2 text-3xl font-bold text-white">Crear pedido</h2>
        <p className="mt-2 text-slate-400">
          Elegí si retirás en el lugar o si necesitás envío a domicilio. El
          pedido se crea en estado PENDIENTE.
        </p>
      </div>

      {formError ? (
        <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-4 text-rose-200">
          {formError}
        </div>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="space-y-5">
          <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-5">
            <h3 className="text-xl font-bold text-white">Tipo de entrega</h3>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <label className="flex cursor-pointer items-start gap-3 rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                <input
                  type="radio"
                  name="tipo_entrega"
                  checked={tipoEntrega === "RETIRO"}
                  onChange={() => setTipoEntrega("RETIRO")}
                  className="mt-1"
                />
                <span>
                  <span className="font-semibold text-white">
                    Retirar en el lugar
                  </span>
                  <span className="mt-1 block text-sm text-slate-400">
                    Sin costo de envío. Permite pagar en efectivo, transferencia
                    o MercadoPago.
                  </span>
                </span>
              </label>
              <label className="flex cursor-pointer items-start gap-3 rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                <input
                  type="radio"
                  name="tipo_entrega"
                  checked={tipoEntrega === "ENVIO"}
                  onChange={() => setTipoEntrega("ENVIO")}
                  className="mt-1"
                />
                <span>
                  <span className="font-semibold text-white">
                    Envío a domicilio
                  </span>
                  <span className="mt-1 block text-sm text-slate-400">
                    Costo de envío {formatMoney(COSTO_ENVIO_DOMICILIO)}. Solo
                    transferencia o MercadoPago.
                  </span>
                </span>
              </label>
            </div>
          </div>

          {tipoEntrega === "ENVIO" ? (
            <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-5">
              <h3 className="text-xl font-bold text-white">
                Dirección de entrega
              </h3>
              {direccionesQuery.isLoading ? (
                <p className="mt-3 text-slate-400">Cargando direcciones...</p>
              ) : null}
              <div className="mt-4 grid gap-3">
                {direcciones.map((direccion) => (
                  <label
                    key={direccion.id}
                    className="flex cursor-pointer items-start gap-3 rounded-2xl border border-white/10 bg-slate-950/50 p-4"
                  >
                    <input
                      type="radio"
                      name="direccion"
                      checked={Number(selectedDireccionId) === direccion.id}
                      onChange={() => setDireccionId(direccion.id)}
                      className="mt-1"
                    />
                    <span>
                      <span className="font-semibold text-white">
                        {direccion.etiqueta ?? "Dirección"}{" "}
                        {direccion.es_principal ? "· Principal" : ""}
                      </span>
                      <span className="mt-1 block text-sm text-slate-400">
                        {direccion.linea1}
                        {direccion.linea2 ? `, ${direccion.linea2}` : ""} ·{" "}
                        {direccion.ciudad}
                      </span>
                    </span>
                  </label>
                ))}
              </div>

              <form
                className="mt-5 rounded-2xl border border-white/10 bg-white/5 p-4"
                onSubmit={crearDireccionRapida}
              >
                <h4 className="font-bold text-white">Crear dirección rápida</h4>
                <div className="mt-3 grid gap-3 md:grid-cols-2">
                  <input
                    value={direccionForm.etiqueta ?? ""}
                    onChange={(e) =>
                      setDireccionForm((f) => ({
                        ...f,
                        etiqueta: e.target.value,
                      }))
                    }
                    placeholder="Alias: Casa, Trabajo"
                    className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
                  />
                  <input
                    value={direccionForm.ciudad}
                    onChange={(e) =>
                      setDireccionForm((f) => ({
                        ...f,
                        ciudad: e.target.value,
                      }))
                    }
                    placeholder="Ciudad"
                    className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
                  />
                  <input
                    value={direccionForm.linea1}
                    onChange={(e) =>
                      setDireccionForm((f) => ({
                        ...f,
                        linea1: e.target.value,
                      }))
                    }
                    placeholder="Dirección principal"
                    className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none md:col-span-2"
                  />
                  <input
                    value={direccionForm.linea2 ?? ""}
                    onChange={(e) =>
                      setDireccionForm((f) => ({
                        ...f,
                        linea2: e.target.value,
                      }))
                    }
                    placeholder="Piso, dpto, referencia"
                    className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none md:col-span-2"
                  />
                </div>
                <button
                  type="submit"
                  disabled={crearDireccionMutation.isPending}
                  className="mt-3 rounded-2xl border border-white/10 px-4 py-3 font-semibold text-slate-100 hover:bg-white/10 disabled:opacity-50"
                >
                  Guardar dirección
                </button>
              </form>
            </div>
          ) : (
            <div className="rounded-3xl border border-emerald-500/20 bg-emerald-500/10 p-5 text-emerald-100">
              <h3 className="text-xl font-bold text-white">
                Retiro en el lugar
              </h3>
              <p className="mt-2">
                No hace falta cargar dirección y el costo de envío queda en{" "}
                {formatMoney(0)}.
              </p>
              <div className="mt-4 rounded-2xl border border-emerald-300/20 bg-slate-950/30 p-4">
                <p className="text-sm font-semibold uppercase tracking-wide text-emerald-200">
                  Dónde retirar
                </p>
                <p className="mt-2 text-white">
                  {domicilioRetiro ||
                    "El comercio todavía no cargó domicilio de retiro."}
                </p>
              </div>
            </div>
          )}

          <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-5">
            <h3 className="text-xl font-bold text-white">
              Forma de pago y notas
            </h3>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <select
                value={formaPagoCodigo}
                onChange={(e) => setFormaPagoCodigo(e.target.value)}
                className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
              >
                {formasPagoDisponibles.map((forma) => (
                  <option key={forma.codigo} value={forma.codigo}>
                    {forma.nombre}
                  </option>
                ))}
              </select>
              <input
                value={notas}
                onChange={(e) => setNotas(e.target.value)}
                placeholder="Notas para el pedido"
                className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
              />
            </div>
            {tipoEntrega === "ENVIO" ? (
              <p className="mt-3 text-sm text-slate-400">
                Para envío a domicilio se oculta Efectivo y solo se permite
                Transferencia o MercadoPago.
              </p>
            ) : null}
            {mostrarDatosTransferencia ? (
              <div className="mt-4 rounded-2xl border border-sky-400/20 bg-sky-500/10 p-4 text-sm text-sky-100">
                <p className="font-semibold text-white">
                  Datos para transferir
                </p>
                <div className="mt-2 grid gap-1 text-sky-100/90">
                  {empresaConfig?.banco ? (
                    <p>Banco: {empresaConfig.banco}</p>
                  ) : null}
                  {empresaConfig?.titular ? (
                    <p>Titular: {empresaConfig.titular}</p>
                  ) : null}
                  {empresaConfig?.cuit ? (
                    <p>CUIT: {empresaConfig.cuit}</p>
                  ) : null}
                  {empresaConfig?.cbu ? (
                    <p>CBU / CVU: {empresaConfig.cbu}</p>
                  ) : null}
                  {empresaConfig?.alias ? (
                    <p>Alias: {empresaConfig.alias}</p>
                  ) : null}
                  {empresaConfig?.instrucciones_transferencia ? (
                    <p className="mt-2 text-sky-50">
                      {empresaConfig.instrucciones_transferencia}
                    </p>
                  ) : null}
                  {!empresaConfig?.banco &&
                  !empresaConfig?.cbu &&
                  !empresaConfig?.alias ? (
                    <p>El comercio todavía no cargó los datos bancarios.</p>
                  ) : null}
                </div>
              </div>
            ) : null}
          </div>
        </div>

        <div className="space-y-4">
          <CartSummary
            showCheckoutAction={false}
            costoEnvio={costoEnvio}
            envioLabel={
              tipoEntrega === "ENVIO"
                ? "Envío a domicilio"
                : "Retiro en el lugar"
            }
          />
          <button
            type="button"
            onClick={confirmarPedido}
            disabled={crearPedidoMutation.isPending}
            className="w-full rounded-2xl bg-emerald-500 px-4 py-3 font-semibold text-white hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {crearPedidoMutation.isPending
              ? "Creando pedido..."
              : `Crear pedido por ${formatMoney(totalPedido)}`}
          </button>
        </div>
      </div>
    </section>
  );
}
