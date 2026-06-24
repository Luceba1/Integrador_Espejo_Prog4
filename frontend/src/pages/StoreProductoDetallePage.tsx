import { Link, useParams } from "react-router-dom";

import ProductCard from "../components/store/ProductCard";
import { useProducto } from "../hooks/useProductos";

function formatMoney(value: number) {
  return new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" }).format(value);
}

export default function StoreProductoDetallePage() {
  const params = useParams();
  const id = Number(params.id);
  const productoQuery = useProducto(id);
  const ingredientesAlergenos = productoQuery.data
    ? (productoQuery.data.ingredientes_configurados?.map((config) => config.ingrediente).filter(Boolean) ?? productoQuery.data.ingredientes)
        .filter((ingrediente, index, array) =>
          Boolean(ingrediente?.es_alergeno) && array.findIndex((item) => item?.id === ingrediente?.id) === index
        )
    : [];

  return (
    <section className="space-y-6">
      <Link to="/store" className="inline-flex items-center gap-2 rounded-2xl border border-emerald-400/30 bg-emerald-500/15 px-4 py-3 font-bold text-emerald-100 shadow-lg shadow-emerald-950/30 transition hover:bg-emerald-500/25 hover:text-white">
        ← Volver
      </Link>

      {productoQuery.isLoading ? <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-slate-300">Cargando producto...</div> : null}
      {productoQuery.isError ? (
        <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-rose-200">
          {productoQuery.error instanceof Error ? productoQuery.error.message : "No se pudo cargar el producto."}
        </div>
      ) : null}

      {productoQuery.data ? (
        <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
          <ProductCard producto={productoQuery.data} />
          <div className="rounded-3xl border border-white/10 bg-slate-900/70 p-6">
            <p className="text-sm font-semibold uppercase tracking-[0.25em] text-emerald-300">Detalle</p>
            <h2 className="mt-2 text-3xl font-bold text-white">{productoQuery.data.nombre}</h2>
            <p className="mt-4 text-slate-300">{productoQuery.data.descripcion ?? "Sin descripción."}</p>
            <p className="mt-5 text-3xl font-bold text-emerald-300">{formatMoney(Number(productoQuery.data.precio_base))}</p>

            {ingredientesAlergenos.length ? (
              <div className="mt-6 rounded-2xl border border-amber-400/30 bg-amber-500/10 p-4 text-amber-100">
                <h3 className="font-bold">⚠️ Advertencia de alérgenos</h3>
                <p className="mt-2 text-sm text-amber-100/85">
                  Este producto contiene: {ingredientesAlergenos.map((ingrediente) => ingrediente?.nombre).join(", ")}.
                </p>
              </div>
            ) : null}

            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                <h3 className="font-bold text-white">Categorías relacionadas</h3>
                <div className="mt-3 flex flex-wrap gap-2">
                  {productoQuery.data.categorias.length ? productoQuery.data.categorias.map((categoria) => (
                    <span key={categoria.id} className="rounded-full bg-sky-500/15 px-3 py-1 text-xs font-semibold text-sky-200">{categoria.nombre}</span>
                  )) : <span className="text-sm text-slate-500">Sin categorías</span>}
                </div>
              </div>
              <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
                <h3 className="font-bold text-white">Ingredientes</h3>
                <div className="mt-3 flex flex-wrap gap-2">
                  {productoQuery.data.ingredientes.length ? productoQuery.data.ingredientes.map((ingrediente) => (
                    <span key={ingrediente.id} className={ingrediente.es_alergeno ? "rounded-full bg-amber-500/15 px-3 py-1 text-xs font-semibold text-amber-200" : "rounded-full bg-purple-500/15 px-3 py-1 text-xs font-semibold text-purple-200"}>
                      {ingrediente.nombre}{ingrediente.es_alergeno ? " · alérgeno" : ""}
                    </span>
                  )) : <span className="text-sm text-slate-500">Sin ingredientes</span>}
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}
