import { Link } from "react-router-dom";

import { useCarrito } from "../../hooks/useCarrito";

function formatMoney(value: number) {
  return new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" }).format(value);
}

export default function CartSummary() {
  const { subtotal, totalItems, hasItems } = useCarrito();
  const costoEnvio = hasItems ? 500 : 0;
  const total = subtotal + costoEnvio;

  return (
    <aside className="rounded-3xl border border-white/10 bg-slate-900/70 p-5">
      <h2 className="text-xl font-bold text-white">Resumen</h2>
      <div className="mt-5 space-y-3 text-sm">
        <div className="flex justify-between text-slate-300">
          <span>Productos</span>
          <span>{totalItems}</span>
        </div>
        <div className="flex justify-between text-slate-300">
          <span>Subtotal</span>
          <span>{formatMoney(subtotal)}</span>
        </div>
        <div className="flex justify-between text-slate-300">
          <span>Envío demo</span>
          <span>{formatMoney(costoEnvio)}</span>
        </div>
        <div className="border-t border-white/10 pt-3">
          <div className="flex justify-between text-lg font-bold text-emerald-300">
            <span>Total</span>
            <span>{formatMoney(total)}</span>
          </div>
        </div>
      </div>

      <Link
        to="/store/checkout"
        className={`mt-5 block rounded-2xl px-4 py-3 text-center font-semibold ${hasItems ? "bg-emerald-500 text-white hover:bg-emerald-400" : "pointer-events-none bg-slate-700 text-slate-400"}`}
      >
        Realizar pedido
      </Link>
    </aside>
  );
}
