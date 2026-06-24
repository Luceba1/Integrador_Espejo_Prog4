import type { Categoria } from "../../types/categoria";

export interface CategoriaTableProps {
  items: Categoria[];
  canManage?: boolean;
  onEdit: (categoria: Categoria) => void;
  onDelete: (categoria: Categoria) => void;
  onCreateChild?: (categoria: Categoria) => void;
  onActivate?: (categoria: Categoria) => void;
  page?: number;
  pageSize?: number;
}

type CategoriaNode = Categoria & { hijos: CategoriaNode[] };
type CategoriaTreeRow = { node: CategoriaNode; depth: number; parentTrail: boolean[]; isLast: boolean };

function buildTree(items: Categoria[]): CategoriaNode[] {
  const map = new Map<number, CategoriaNode>();
  items.forEach((categoria) => map.set(categoria.id, { ...categoria, hijos: [] }));

  const roots: CategoriaNode[] = [];
  map.forEach((node) => {
    if (node.parent_id && map.has(node.parent_id)) {
      map.get(node.parent_id)!.hijos.push(node);
    } else {
      roots.push(node);
    }
  });

  const sortNodes = (nodes: CategoriaNode[]) => {
    nodes.sort((a, b) => a.nombre.localeCompare(b.nombre));
    nodes.forEach((node) => sortNodes(node.hijos));
  };

  sortNodes(roots);
  return roots;
}

function flattenTree(nodes: CategoriaNode[], depth = 0, parentTrail: boolean[] = []): CategoriaTreeRow[] {
  return nodes.flatMap((node, index) => {
    const isLast = index === nodes.length - 1;
    const current = [{ node, depth, parentTrail, isLast }];
    return [
      ...current,
      ...flattenTree(node.hijos, depth + 1, [...parentTrail, !isLast]),
    ];
  });
}

export default function CategoriaTable({
  items,
  canManage = true,
  onEdit,
  onDelete,
  onCreateChild,
  onActivate,
  page,
  pageSize,
}: CategoriaTableProps) {
  const byId = new Map(items.map((categoria) => [categoria.id, categoria]));
  const allRows = flattenTree(buildTree(items));
  const rows = page && pageSize ? allRows.slice((page - 1) * pageSize, page * pageSize) : allRows;

  return (
    <div className="overflow-hidden rounded-3xl border border-white/10 bg-slate-900/70">
      <div className="border-b border-white/10 bg-slate-950/50 px-5 py-4">
        <h3 className="font-semibold text-white">Árbol de categorías</h3>
        <p className="mt-1 text-sm text-slate-400">
          Las ramas muestran la dependencia padre → hija. Usá “Crear hija” para agregar subcategorías dentro de una rama.
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-white/5 text-slate-300">
            <tr>
              <th className="px-5 py-4">ID</th>
              <th className="px-5 py-4">Imagen</th>
              <th className="px-5 py-4">Categoría</th>
              <th className="px-5 py-4">Descripción</th>
              <th className="px-5 py-4">Padre</th>
              <th className="px-5 py-4 text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(({ node: categoria, depth, parentTrail, isLast }) => {
              const tieneHijos = categoria.hijos.length > 0;
              const padre = categoria.parent_id ? byId.get(categoria.parent_id) : null;
              const isDeleted = Boolean(categoria.deleted_at);

              return (
                <tr key={categoria.id} className={`border-t border-white/5 transition ${isDeleted ? "bg-slate-950/70 text-slate-500" : ""}`}>
                  <td className="px-5 py-4 text-slate-300">{categoria.id}</td>
                  <td className="px-5 py-4">
                    {categoria.imagen_url ? (
                      <img
                        src={categoria.imagen_url}
                        alt={categoria.nombre}
                        className="h-14 w-20 rounded-xl object-cover"
                      />
                    ) : (
                      <span className="text-xs text-slate-500">Sin imagen</span>
                    )}
                  </td>
                  <td className="px-5 py-4 font-semibold text-white">
                    <div className="flex items-center">
                      {parentTrail.map((showLine, index) => (
                        <span
                          key={index}
                          className={`mr-1 h-8 w-5 border-l ${showLine ? "border-blue-400/35" : "border-transparent"}`}
                        />
                      ))}

                      {depth > 0 ? (
                        <span className="mr-2 flex h-8 w-7 items-center">
                          <span className="h-4 border-l border-blue-400/35" />
                          <span className="w-6 border-t border-blue-400/35" />
                          <span className="text-blue-300">{isLast ? "└" : "├"}</span>
                        </span>
                      ) : (
                        <span className="mr-2 inline-flex h-7 w-7 items-center justify-center rounded-full bg-blue-500/15 text-xs text-blue-200">
                          🌳
                        </span>
                      )}

                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <span>{categoria.nombre}</span>
                          {tieneHijos ? (
                            <span className="rounded-full bg-blue-500/15 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-blue-200">
                              Rama
                            </span>
                          ) : (
                            <span className="rounded-full bg-emerald-500/15 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-emerald-200">
                              Final
                            </span>
                          )}
                          {categoria.deleted_at ? (
                            <span className="rounded-full bg-rose-500/15 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-rose-200">
                              Eliminada
                            </span>
                          ) : null}
                        </div>
                        <p className="mt-1 text-xs text-slate-500">
                          Nivel {depth + 1}{tieneHijos ? ` · ${categoria.hijos.length} subcategoría(s)` : " · seleccionable en productos"}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-4 text-slate-300">{categoria.descripcion || "Sin descripción"}</td>
                  <td className="px-5 py-4 text-slate-300">{padre?.nombre ?? "Raíz"}</td>
                  <td className="px-5 py-4">
                    <div className="flex justify-end gap-2">
                      {canManage ? (
                        <>
                          {categoria.deleted_at && onActivate ? (
                            <button
                              type="button"
                              onClick={() => onActivate(categoria)}
                              className="rounded-xl bg-emerald-500 px-3 py-2 font-semibold text-white shadow-lg shadow-emerald-500/20 hover:bg-emerald-400"
                            >
                              Activar
                            </button>
                          ) : null}
                          <button
                            type="button"
                            onClick={() => onCreateChild?.(categoria)}
                            disabled={isDeleted}
                            className={isDeleted ? "cursor-not-allowed rounded-xl bg-slate-800 px-3 py-2 font-medium text-slate-500" : "rounded-xl bg-blue-500/15 px-3 py-2 font-medium text-blue-200 hover:bg-blue-500/25"}
                          >
                            Crear hija
                          </button>
                          <button
                            type="button"
                            onClick={() => onEdit(categoria)}
                            disabled={isDeleted}
                            className={isDeleted ? "cursor-not-allowed rounded-xl bg-slate-800 px-3 py-2 font-medium text-slate-500" : "rounded-xl bg-amber-500/15 px-3 py-2 font-medium text-amber-200 hover:bg-amber-500/25"}
                          >
                            Editar
                          </button>
                          <button
                            type="button"
                            onClick={() => onDelete(categoria)}
                            disabled={isDeleted}
                            className={isDeleted ? "cursor-not-allowed rounded-xl bg-slate-800 px-3 py-2 font-medium text-slate-500" : "rounded-xl bg-rose-500/15 px-3 py-2 font-medium text-rose-200 hover:bg-rose-500/25"}
                          >
                            Eliminar
                          </button>
                        </>
                      ) : (
                        <span className="text-slate-500">Solo lectura</span>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
            {!rows.length ? (
              <tr>
                <td colSpan={6} className="px-5 py-10 text-center text-slate-400">
                  No hay categorías cargadas.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
