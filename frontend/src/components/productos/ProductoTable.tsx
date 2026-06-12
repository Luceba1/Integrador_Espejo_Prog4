import { Link } from "react-router-dom";

import type { Producto } from "../../types/producto";

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
            {items.map((producto) => (
              <tr key={producto.id} className={`border-t border-white/5 align-top transition ${producto.deleted_at ? "bg-slate-950/70 opacity-50 grayscale" : ""}`}>
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
                  ${Number(producto.precio_base).toFixed(2)}
                  {producto.unidad_venta ? <span className="ml-1 text-xs text-slate-500">/ {producto.unidad_venta.simbolo}</span> : null}
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
                      to={`/admin/productos/${producto.id}`}
                      className="rounded-xl bg-sky-500/15 px-3 py-2 font-medium text-sky-200 hover:bg-sky-500/25"
                    >
                      Ver detalle
                    </Link>
                    {/* El stock del producto ahora se calcula automáticamente desde la receta de ingredientes. */}
                    {canManageStock && onToggleDisponibilidad ? (
                      <button
                        type="button"
                        onClick={() => onToggleDisponibilidad(producto)}
                        className="rounded-xl bg-indigo-500/15 px-3 py-2 font-medium text-indigo-200 hover:bg-indigo-500/25"
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
                            className="rounded-xl bg-emerald-500/15 px-3 py-2 font-medium text-emerald-200 hover:bg-emerald-500/25"
                          >
                            Activar
                          </button>
                        ) : null}
                        <button
                          type="button"
                          onClick={() => onEdit(producto)}
                          className="rounded-xl bg-amber-500/15 px-3 py-2 font-medium text-amber-200 hover:bg-amber-500/25"
                        >
                          Editar
                        </button>
                        <button
                          type="button"
                          onClick={() => onDelete(producto)}
                          className="rounded-xl bg-rose-500/15 px-3 py-2 font-medium text-rose-200 hover:bg-rose-500/25"
                        >
                          Eliminar
                        </button>
                      </>
                    ) : null}
                  </div>
                </td>
              </tr>
            ))}
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
