import type { Producto } from "../../types/producto";

interface ProductoDetailCardProps {
  producto: Producto;
}

export default function ProductoDetailCard({ producto }: ProductoDetailCardProps) {
  return (
    <div className="grid gap-6 lg:grid-cols-[2fr_1fr_1fr]">
      <article className="rounded-3xl border border-white/10 bg-white/5 p-6">
        <p className="text-sm uppercase tracking-[0.3em] text-sky-300">Producto</p>
        <h3 className="mt-2 text-3xl font-bold text-white">{producto.nombre}</h3>
        <p className="mt-4 text-sm text-slate-300">{producto.descripcion || "Este producto no tiene descripción."}</p>
        <div className="mt-6 flex flex-wrap gap-3">
          <span className="inline-flex rounded-full bg-emerald-500/15 px-4 py-2 text-sm font-semibold text-emerald-300">
            Precio: ${Number(producto.precio_base).toFixed(2)}
          </span>
          <span className="inline-flex rounded-full bg-sky-500/15 px-4 py-2 text-sm font-semibold text-sky-200">
            Sugerido: ${Number(producto.precio_sugerido ?? 0).toFixed(2)}
          </span>
          <span className="inline-flex rounded-full bg-white/10 px-4 py-2 text-sm font-semibold text-slate-200">
            Costo: ${Number(producto.costo_ingredientes ?? 0).toFixed(2)} · Margen: {Number(producto.margen_ganancia_porcentaje ?? 0).toFixed(2)}%
          </span>
          <span className="inline-flex rounded-full bg-sky-500/15 px-4 py-2 text-sm font-semibold text-sky-200">
            Preparables: {producto.stock_cantidad} unidades
          </span>
        </div>
      </article>

      <article className="rounded-3xl border border-white/10 bg-white/5 p-6">
        <h4 className="text-lg font-semibold text-white">Categorías</h4>
        <ul className="mt-4 space-y-3">
          {producto.categorias.length ? (
            producto.categorias.map((categoria) => (
              <li key={categoria.id} className="rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-3 text-slate-200">
                {categoria.nombre}
              </li>
            ))
          ) : <li className="text-sm text-slate-400">Sin categorías asociadas.</li>}
        </ul>
      </article>

      <article className="rounded-3xl border border-white/10 bg-white/5 p-6">
        <h4 className="text-lg font-semibold text-white">Receta</h4>
        <ul className="mt-4 space-y-3">
          {producto.ingredientes_configurados?.length ? (
            producto.ingredientes_configurados.map((config) => (
              <li key={config.ingrediente_id} className="rounded-2xl border border-white/10 bg-slate-950/50 px-4 py-3 text-slate-200">
                <p className="font-semibold">{config.ingrediente?.nombre ?? `Ingrediente #${config.ingrediente_id}`}</p>
                <p className="mt-1 text-xs text-slate-400">
                  Consume: {config.cantidad}{config.unidad_medida ? ` ${config.unidad_medida.simbolo}` : ""} por unidad · Costo: ${Number((config.ingrediente?.precio_por_unidad ?? 0) * Number(config.cantidad)).toFixed(2)}
                </p>
              </li>
            ))
          ) : <li className="text-sm text-slate-400">Sin receta configurada.</li>}
        </ul>
      </article>
    </div>
  );
}
