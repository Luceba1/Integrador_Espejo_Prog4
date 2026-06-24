import { Link } from "react-router-dom";

import type { Producto } from "../../types/producto";

function formatMoney(value: number | undefined) {
  return `$${Number(value ?? 0).toFixed(2)}`;
}

export interface ProductoTableProps {
  items: Producto[];
  canManage?: boolean;
  canManageStock?: boolean;
  onEdit: (producto: Producto) => void;
  onDelete: (producto: Producto) => void;
  onToggleDisponibilidad?: (producto: Producto) => void;
  onUpdateStock?: (producto: Producto) => void;
  onActivate?: (producto: Producto) => void;
}

export default function ProductoTable({
  items,
  canManage = true,
  canManageStock = false,
  onEdit,
  onDelete,
  onToggleDisponibilidad,
  onUpdateStock,
  onActivate,
}: ProductoTableProps) {
  return (
    <div className="overflow-hidden rounded-3xl border border-white/10 bg-slate-900/70">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-white/5 text-slate-300">
            <tr>
              <th className="px-5 py-4">ID</th>
              <th className="px-5 py-4">Imagen</th>
              <th className="px-5 py-4">Nombre</th>
              <th className="px-5 py-4">Precio</th>
              <th className="px-5 py-4">Preparables</th>
              <th className="px-5 py-4">Relaciones</th>
              <th className="px-5 py-4 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((producto) => {
              const isDeleted = Boolean(producto.deleted_at);
              return (
              <tr key={producto.id} className={`border-t border-white/5 align-top transition ${isDeleted ? "bg-slate-950/70 text-slate-500" : ""}`}>
                <td className="px-5 py-4 text-slate-300">{producto.id}</td>
                <td className="px-5 py-4">
                  {producto.imagenes_url?.[0] ? (
                    <img src={producto.imagenes_url[0]} alt={producto.nombre} className="h-16 w-24 rounded-xl object-cover" />
                  ) : (
                    <span className="text-xs text-slate-500">Sin imagen</span>
                  )}
                </td>
                <td className="px-5 py-4">
                  <p className="font-semibold text-white">{producto.nombre}</p>
                  <p className="mt-1 text-xs text-slate-400">{producto.descripcion || "Sin descripción"}</p>
                  <span className={[
                    "mt-3 inline-flex rounded-full px-3 py-1 text-xs font-semibold",
                    producto.disponible ? "bg-emerald-500/15 text-emerald-200" : "bg-rose-500/15 text-rose-200",
                  ].join(" ")}>{producto.disponible ? "Disponible" : "No disponible"}</span>
                  {producto.deleted_at ? (
                    <span className="ml-2 mt-3 inline-flex rounded-full bg-rose-500/15 px-3 py-1 text-xs font-semibold text-rose-200">Eliminado</span>
                  ) : null}
                </td>
                <td className="px-5 py-4 font-semibold text-emerald-300">
                  <p>{formatMoney(producto.precio_base)}</p>
                  <p className="mt-1 text-xs font-normal text-slate-400">Sugerido: {formatMoney(producto.precio_sugerido)}</p>
                  <p className="mt-1 text-xs font-normal text-slate-500">Costo: {formatMoney(producto.costo_ingredientes)} · Margen {Number(producto.margen_ganancia_porcentaje ?? 0).toFixed(2)}%</p>
                </td>
                <td className="px-5 py-4 text-slate-300">{producto.stock_cantidad} unidades</td>
                <td className="px-5 py-4 text-slate-300">
                  <p>
                    <span className="text-slate-500">Categorías: </span>
                    {producto.categorias.length
                      ? producto.categorias.map((categoria) => categoria.nombre).join(", ")
                      : "Sin categorías"}
                  </p>
                  <p className="mt-2">
                    <span className="text-slate-500">Ingredientes: </span>
                    {producto.ingredientes.length
                      ? producto.ingredientes.map((ingrediente) => ingrediente.nombre).join(", ")
                      : "Sin ingredientes"}
                  </p>
                </td>
                <td className="px-5 py-4">
                  <div className="flex flex-wrap justify-end gap-2">
                    <Link
                      to={isDeleted ? "#" : `/admin/productos/${producto.id}`}
                      onClick={(event) => { if (isDeleted) event.preventDefault(); }}
                      className={isDeleted ? "cursor-not-allowed rounded-xl bg-slate-800 px-3 py-2 font-medium text-slate-500" : "rounded-xl bg-sky-500/15 px-3 py-2 font-medium text-sky-200 hover:bg-sky-500/25"}
                    >
                      Ver detalle
                    </Link>
                    {/* El stock del producto ahora se calcula automáticamente desde la receta de ingredientes. */}
                    {canManageStock && onToggleDisponibilidad ? (
                      <button
                        type="button"
                        onClick={() => onToggleDisponibilidad(producto)}
                        disabled={isDeleted}
                        className={isDeleted ? "cursor-not-allowed rounded-xl bg-slate-800 px-3 py-2 font-medium text-slate-500" : "rounded-xl bg-indigo-500/15 px-3 py-2 font-medium text-indigo-200 hover:bg-indigo-500/25"}
                      >
                        {producto.disponible ? "No disponible" : "Disponible"}
                      </button>
                    ) : null}
                    {canManage ? (
                      <>
                        {producto.deleted_at && onActivate ? (
                          <button
                            type="button"
                            onClick={() => onActivate(producto)}
                            className="rounded-xl bg-emerald-500 px-3 py-2 font-semibold text-white shadow-lg shadow-emerald-500/20 hover:bg-emerald-400"
                          >
                            Activar
                          </button>
                        ) : null}
                        <button
                          type="button"
                          onClick={() => onEdit(producto)}
                          disabled={isDeleted}
                          className={isDeleted ? "cursor-not-allowed rounded-xl bg-slate-800 px-3 py-2 font-medium text-slate-500" : "rounded-xl bg-amber-500/15 px-3 py-2 font-medium text-amber-200 hover:bg-amber-500/25"}
                        >
                          Editar
                        </button>
                        <button
                          type="button"
                          onClick={() => onDelete(producto)}
                          disabled={isDeleted}
                          className={isDeleted ? "cursor-not-allowed rounded-xl bg-slate-800 px-3 py-2 font-medium text-slate-500" : "rounded-xl bg-rose-500/15 px-3 py-2 font-medium text-rose-200 hover:bg-rose-500/25"}
                        >
                          Eliminar
                        </button>
                      </>
                    ) : null}
                  </div>
                </td>
              </tr>
              );
            })}
            {!items.length ? (
              <tr>
                <td colSpan={7} className="px-5 py-10 text-center text-slate-400">
                  No hay productos cargados.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
