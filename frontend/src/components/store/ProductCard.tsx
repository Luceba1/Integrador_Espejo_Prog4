import { useState } from "react";
import { Link } from "react-router-dom";

import { useCarrito } from "../../hooks/useCarrito";
import type { Producto } from "../../types/producto";
import { useUiStore } from "../../stores/uiStore";

function formatMoney(value: number) {
  return new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" }).format(value);
}

export default function ProductCard({ producto }: { producto: Producto }) {
  const { addProducto, items } = useCarrito();
  const showToast = useUiStore((state) => state.showToast);
  const [added, setAdded] = useState(false);
  const imageUrl = producto.imagenes_url?.[0];
  const canAdd = producto.disponible && producto.stock_cantidad > 0;
  const itemEnCarrito = items.find((item) => item.producto_id === producto.id);
  const cantidadEnCarrito = itemEnCarrito?.cantidad ?? 0;
  const reachedLimit = cantidadEnCarrito >= producto.stock_cantidad;
  const ingredientesAlergenos = (
    producto.ingredientes_configurados?.map((config) => config.ingrediente).filter(Boolean) ?? producto.ingredientes
  ).filter((ingrediente, index, array) =>
    Boolean(ingrediente?.es_alergeno) && array.findIndex((item) => item?.id === ingrediente?.id) === index
  );

  function handleAdd() {
    if (!canAdd || reachedLimit) return;
    addProducto(producto, 1);
    showToast("success", `${producto.nombre} agregado al carrito.`);
    setAdded(true);
    window.setTimeout(() => setAdded(false), 1200);
  }

  return (
    <article className={`relative flex h-full flex-col overflow-hidden rounded-3xl border bg-slate-900/70 transition ${added ? "border-emerald-400 shadow-lg shadow-emerald-500/20" : "border-white/10"}`}>
      {added ? (
        <div className="absolute right-3 top-3 z-10 rounded-full bg-emerald-500 px-3 py-1 text-xs font-bold text-white shadow-lg">
          +1 al carrito
        </div>
      ) : null}

      <div className="flex h-44 items-center justify-center bg-slate-800">
        {imageUrl ? <img src={imageUrl} alt={producto.nombre} className="h-full w-full object-cover" /> : <span className="text-sm text-slate-500">Sin imagen</span>}
      </div>

      <div className="flex flex-1 flex-col p-5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="text-lg font-bold text-white">{producto.nombre}</h3>
            <p className="mt-1 line-clamp-2 text-sm text-slate-400">{producto.descripcion ?? "Sin descripción"}</p>
          </div>
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${canAdd ? "bg-emerald-500/15 text-emerald-200" : "bg-rose-500/15 text-rose-200"}`}>
            {canAdd ? "Disponible" : "No disponible"}
          </span>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {producto.categorias.slice(0, 2).map((categoria) => (
            <span key={categoria.id} className="rounded-full bg-sky-500/15 px-3 py-1 text-xs font-semibold text-sky-200">
              {categoria.nombre}
            </span>
          ))}
        </div>

        {ingredientesAlergenos.length ? (
          <div className="mt-4 rounded-2xl border border-amber-400/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
            <p className="font-bold">⚠️ Contiene alérgenos</p>
            <p className="mt-1 text-xs text-amber-100/80">
              {ingredientesAlergenos.map((ingrediente) => ingrediente?.nombre).join(", ")}
            </p>
          </div>
        ) : null}

        <div className="mt-auto pt-5">
          <p className="text-2xl font-bold text-emerald-300">
            {formatMoney(Number(producto.precio_base))}
          </p>
          <div className="mt-1 flex items-center justify-between gap-3 text-xs text-slate-500">
            <span>Se pueden preparar: {producto.stock_cantidad} unidades</span>
            {cantidadEnCarrito > 0 ? <span className="inline-flex shrink-0 items-center gap-1 whitespace-nowrap rounded-full bg-emerald-500/10 px-2.5 py-1 font-semibold text-emerald-200"><span>En carrito:</span><span>{cantidadEnCarrito}</span></span> : null}
          </div>

          <div className="mt-4 grid gap-2 sm:grid-cols-2">
            <Link to={`/store/productos/${producto.id}`} className="rounded-2xl border border-white/10 px-4 py-3 text-center text-sm font-semibold text-slate-100 hover:bg-white/10">
              Ver detalle
            </Link>
            <button
              type="button"
              onClick={handleAdd}
              disabled={!canAdd || reachedLimit}
              className={`rounded-2xl px-4 py-3 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-50 ${added ? "bg-emerald-600" : "bg-emerald-500 hover:bg-emerald-400"}`}
            >
              {reachedLimit && canAdd ? "Máximo" : added ? "Agregado ✓" : "Agregar"}
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}
