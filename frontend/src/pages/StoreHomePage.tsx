import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import ProductCard from "../components/store/ProductCard";
import { useProductos } from "../hooks/useProductos";

const PAGE_SIZE = 8;

export default function StoreHomePage() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get("q")?.trim() ?? "";
  const [page, setPage] = useState(1);
  const productosQuery = useProductos(query, page, PAGE_SIZE, { disponible: true });
  const canGoNext = useMemo(() => (productosQuery.data?.length ?? 0) === PAGE_SIZE, [productosQuery.data]);

  useEffect(() => {
    setPage(1);
  }, [query]);

  return (
    <section className="space-y-6">
      <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-emerald-500/20 to-sky-500/10 p-8">
        <p className="text-sm font-semibold uppercase tracking-[0.25em] text-emerald-200">Catálogo</p>
        <h2 className="mt-3 text-4xl font-bold text-white">Productos disponibles</h2>
        <p className="mt-3 max-w-2xl text-slate-300">
          Productos reales del backend, filtrados por disponibilidad. El carrito queda persistido con Zustand + localStorage.
        </p>
        {query ? (
          <p className="mt-4 rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-3 text-sm text-slate-200">
            Resultado de búsqueda para <span className="font-semibold text-emerald-300">{query}</span>
          </p>
        ) : null}
      </div>

      {productosQuery.isLoading ? <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-slate-300">Cargando productos...</div> : null}

      {productosQuery.isError ? (
        <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-rose-200">
          {productosQuery.error instanceof Error ? productosQuery.error.message : "No se pudo cargar el catálogo."}
        </div>
      ) : null}

      {productosQuery.data ? (
        <>
          <div className="space-y-5">
            <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
              {productosQuery.data.map((producto) => <ProductCard key={producto.id} producto={producto} />)}
            </div>

            {!productosQuery.data.length ? (
              <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-center text-slate-400">No hay productos disponibles.</div>
            ) : null}
          </div>

          <div className="flex items-center justify-between rounded-3xl border border-white/10 bg-white/5 px-5 py-4">
            <button
              type="button"
              onClick={() => setPage((current) => Math.max(1, current - 1))}
              disabled={page === 1 || productosQuery.isFetching}
              className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10 disabled:opacity-50"
            >
              Página anterior
            </button>
            <p className="text-sm text-slate-300">Página {page}</p>
            <button
              type="button"
              onClick={() => setPage((current) => current + 1)}
              disabled={!canGoNext || productosQuery.isFetching}
              className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10 disabled:opacity-50"
            >
              Página siguiente
            </button>
          </div>
        </>
      ) : null}
    </section>
  );
}
