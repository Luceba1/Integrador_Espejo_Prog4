import { Link } from "react-router-dom";

import { useCarrito } from "../../hooks/useCarrito";

function formatMoney(value: number) {
  return new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" }).format(value);
}

export default function FloatingCartPanel() {
  const { items, subtotal, totalItems, hasItems, updateCantidad, removeItem } = useCarrito();
  const costoEnvio = hasItems ? 500 : 0;
  const total = subtotal + costoEnvio;

  return (
    <aside className="sticky top-6 overflow-hidden rounded-3xl border border-emerald-400/20 bg-slate-900/95 shadow-2xl shadow-emerald-950/30">
      <div className="border-b border-white/10 bg-gradient-to-r from-emerald-500/20 to-sky-500/10 p-5">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-200">Carrito en vivo</p>
        <div className="mt-2 flex items-end justify-between gap-3">
          <h2 className="text-2xl font-bold text-white">{totalItems} item{totalItems === 1 ? "" : "s"}</h2>
          <span className="rounded-full bg-emerald-500 px-3 py-1 text-sm font-bold text-white">{formatMoney(total)}</span>
        </div>
      </div>

      <div className="max-h-[430px] space-y-3 overflow-y-auto p-4">
        {items.map((item) => (
          <div key={item.producto_id} className="rounded-2xl border border-white/10 bg-slate-950/60 p-3">
            <div className="flex gap-3">
              {item.imagen_url ? (
                <img src={item.imagen_url} alt={item.nombre} className="h-14 w-16 rounded-xl object-cover" />
              ) : (
                <div className="flex h-14 w-16 items-center justify-center rounded-xl bg-slate-800 text-xs text-slate-500">Sin img</div>
              )}
              <div className="min-w-0 flex-1">
                <p className="truncate font-semibold text-white">{item.nombre}</p>
                <p className="text-xs text-slate-400">{formatMoney(item.precio_unitario)} c/u</p>
                <p className="mt-1 text-sm font-semibold text-emerald-300">{formatMoney(item.precio_unitario * item.cantidad)}</p>
              </div>
            </div>

            <div className="mt-3 flex items-center justify-between gap-2">
              <div className="flex items-center overflow-hidden rounded-full border border-white/10">
                <button type="button" onClick={() => updateCantidad(item.producto_id, item.cantidad - 1)} className="px-3 py-1 text-slate-200 hover:bg-white/10">−</button>
                <span className="min-w-10 px-3 py-1 text-center text-sm font-bold text-white">{item.cantidad}</span>
                <button type="button" onClick={() => updateCantidad(item.producto_id, item.cantidad + 1)} className="px-3 py-1 text-slate-200 hover:bg-white/10">+</button>
              </div>
              <button type="button" onClick={() => removeItem(item.producto_id)} className="rounded-full px-3 py-1 text-xs font-semibold text-rose-200 hover:bg-rose-500/10">Quitar</button>
            </div>
          </div>
        ))}

        {!items.length ? (
          <div className="rounded-2xl border border-dashed border-white/10 p-6 text-center text-sm text-slate-400">
            Agregá productos y vas a ver el carrito actualizarse acá en tiempo real.
          </div>
        ) : null}
      </div>

      <div className="border-t border-white/10 p-4">
        <div className="space-y-2 text-sm">
          <div className="flex justify-between text-slate-300"><span>Subtotal</span><span>{formatMoney(subtotal)}</span></div>
          <div className="flex justify-between text-slate-300"><span>Envío demo</span><span>{formatMoney(costoEnvio)}</span></div>
        </div>
        <Link to="/store/checkout" className={`mt-4 block rounded-2xl px-4 py-3 text-center font-semibold ${hasItems ? "bg-emerald-500 text-white hover:bg-emerald-400" : "pointer-events-none bg-slate-700 text-slate-400"}`}>
          Ir a pagar
        </Link>
      </div>
    </aside>
  );
}
