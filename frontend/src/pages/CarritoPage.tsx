import { Link } from "react-router-dom";

import CartSummary from "../components/store/CartSummary";
import { useCarrito } from "../hooks/useCarrito";

function formatMoney(value: number) {
  return new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" }).format(value);
}

export default function CarritoPage() {
  const { clearCart, hasItems, items, removeItem, updateCantidad } = useCarrito();

  return (
    <section className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-emerald-300">Carrito</p>
          <h2 className="mt-2 text-3xl font-bold text-white">Tu pedido</h2>
          <p className="mt-2 text-slate-400">Persistencia con Zustand + localStorage: si recargás la página, el carrito se conserva.</p>
        </div>
        {hasItems ? (
          <button type="button" onClick={clearCart} className="rounded-2xl border border-rose-500/30 px-4 py-3 font-semibold text-rose-200 hover:bg-rose-500/10">
            Vaciar carrito
          </button>
        ) : null}
      </div>

      {!hasItems ? (
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-center">
          <p className="text-lg font-semibold text-white">El carrito está vacío.</p>
          <Link to="/store" className="mt-4 inline-block rounded-2xl bg-emerald-500 px-5 py-3 font-semibold text-white hover:bg-emerald-400">
            Ir al catálogo
          </Link>
        </div>
      ) : (
        <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
          <div className="space-y-4">
            {items.map((item) => (
              <article key={item.producto_id} className="rounded-3xl border border-white/10 bg-slate-900/70 p-5">
                <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                  <div className="flex gap-4">
                    <div className="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-2xl bg-slate-800">
                      {item.imagen_url ? <img src={item.imagen_url} alt={item.nombre} className="h-full w-full object-cover" /> : <span className="text-xs text-slate-500">Sin imagen</span>}
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-white">{item.nombre}</h3>
                      <p className="mt-1 text-sm text-slate-400">Precio unitario: {formatMoney(item.precio_unitario)}</p>
                      <p className="mt-1 text-sm text-slate-500">Stock máximo: {item.stock_cantidad}</p>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-3">
                    <input
                      type="number"
                      min={1}
                      max={item.stock_cantidad}
                      value={item.cantidad}
                      onChange={(event) => updateCantidad(item.producto_id, Number(event.target.value))}
                      className="w-24 rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
                    />
                    <p className="min-w-32 text-right font-bold text-emerald-300">{formatMoney(item.precio_unitario * item.cantidad)}</p>
                    <button type="button" onClick={() => removeItem(item.producto_id)} className="rounded-2xl border border-white/10 px-4 py-3 text-sm font-semibold text-slate-200 hover:bg-white/10">
                      Quitar
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
          <CartSummary />
        </div>
      )}
    </section>
  );
}
