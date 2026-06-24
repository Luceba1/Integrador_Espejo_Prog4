import type { Ingrediente } from "../../types/ingrediente";

export interface IngredienteTableProps {
  items: Ingrediente[];
  canManage?: boolean;
  onEdit: (ingrediente: Ingrediente) => void;
  onDelete: (ingrediente: Ingrediente) => void;
  onActivate?: (ingrediente: Ingrediente) => void;
}

function formatStock(ingrediente: Ingrediente) {
  const simbolo = ingrediente.unidad_medida?.simbolo ? ` ${ingrediente.unidad_medida.simbolo}` : "";
  return `${ingrediente.stock_cantidad}${simbolo}`;
}

function formatMoney(value: number | undefined) {
  return `$${Number(value ?? 0).toFixed(2)}`;
}

export default function IngredienteTable({ items, canManage = true, onEdit, onDelete, onActivate }: IngredienteTableProps) {
  return (
    <div className="overflow-hidden rounded-3xl border border-white/10 bg-slate-900/70">
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-white/5 text-slate-300">
            <tr>
              <th className="px-5 py-4">ID</th>
              <th className="px-5 py-4">Nombre</th>
              <th className="px-5 py-4">Stock</th>
              <th className="px-5 py-4">Costo</th>
              <th className="px-5 py-4">Precio x unidad</th>
              <th className="px-5 py-4">Descripción</th>
              <th className="px-5 py-4">Alérgeno</th>
              <th className="px-5 py-4 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((ingrediente) => {
              const isDeleted = Boolean(ingrediente.deleted_at);
              return (
              <tr key={ingrediente.id} className={`border-t border-white/5 transition ${isDeleted ? "bg-slate-950/70 text-slate-500" : ""}`}>
                <td className="px-5 py-4 text-slate-300">{ingrediente.id}</td>
                <td className="px-5 py-4 font-semibold text-white">{ingrediente.nombre}{ingrediente.deleted_at ? <span className="ml-2 rounded-full bg-rose-500/15 px-2 py-1 text-xs text-rose-200">Eliminado</span> : null}</td>
                <td className="px-5 py-4 font-semibold text-emerald-200">{formatStock(ingrediente)}</td>
                <td className="px-5 py-4 text-slate-300">{formatMoney(ingrediente.precio_costo_total)}</td>
                <td className="px-5 py-4 text-slate-300">{formatMoney(ingrediente.precio_por_unidad)}</td>
                <td className="px-5 py-4 text-slate-300">{ingrediente.descripcion || "Sin descripción"}</td>
                <td className="px-5 py-4 text-slate-300">{ingrediente.es_alergeno ? "Sí" : "No"}</td>
                <td className="px-5 py-4">
                  <div className="flex justify-end gap-2">
                    {canManage ? (
                      <>
                        {ingrediente.deleted_at && onActivate ? <button type="button" onClick={() => onActivate(ingrediente)} className="rounded-xl bg-emerald-500 px-3 py-2 font-semibold text-white shadow-lg shadow-emerald-500/20 hover:bg-emerald-400">Activar</button> : null}
                        <button type="button" onClick={() => onEdit(ingrediente)} disabled={isDeleted} className={isDeleted ? "cursor-not-allowed rounded-xl bg-slate-800 px-3 py-2 font-medium text-slate-500" : "rounded-xl bg-amber-500/15 px-3 py-2 font-medium text-amber-200 hover:bg-amber-500/25"}>Editar</button>
                        <button type="button" onClick={() => onDelete(ingrediente)} disabled={isDeleted} className={isDeleted ? "cursor-not-allowed rounded-xl bg-slate-800 px-3 py-2 font-medium text-slate-500" : "rounded-xl bg-rose-500/15 px-3 py-2 font-medium text-rose-200 hover:bg-rose-500/25"}>Eliminar</button>
                      </>
                    ) : <span className="text-slate-500">Solo lectura</span>}
                  </div>
                </td>
              </tr>
              );
            })}
            {!items.length ? <tr><td colSpan={8} className="px-5 py-10 text-center text-slate-400">No hay ingredientes cargados.</td></tr> : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
