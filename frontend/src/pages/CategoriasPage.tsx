import { useEffect, useState } from "react";

import CategoriaModal from "../components/categorias/CategoriaModal";
import CategoriaTable from "../components/categorias/CategoriaTable";
import PageContainer from "../components/layout/PageContainer";
import { useAuth } from "../hooks/useAuth";
import {
  useActualizarCategoria,
  useActivarCategoria,
  useCategorias,
  useCrearCategoria,
  useEliminarCategoria,
} from "../hooks/useCategorias";
import { descargarExcel } from "../services/exportService";
import type { Categoria, CategoriaPayload } from "../types/categoria";

const PAGE_SIZE = 10;

export default function CategoriasPage() {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<Categoria | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [defaultParentId, setDefaultParentId] = useState<number | null>(null);
  const [page, setPage] = useState(1);
  const [incluirEliminadas, setIncluirEliminadas] = useState(false);
  const [soloRaiz, setSoloRaiz] = useState(false);
  const [search, setSearch] = useState("");
  const [currentSearch, setCurrentSearch] = useState("");
  const [exportando, setExportando] = useState(false);

  const { hasRole } = useAuth();
  const canManage = hasRole("ADMIN");

  const categoriasQuery = useCategorias({
    full: true,
    incluir_eliminadas: incluirEliminadas,
    solo_raiz: soloRaiz,
    search: currentSearch,
  });
  const crearMutation = useCrearCategoria();
  const actualizarMutation = useActualizarCategoria();
  const eliminarMutation = useEliminarCategoria();
  const activarMutation = useActivarCategoria();
  const deleting = eliminarMutation.isPending;
  const totalCategorias = categoriasQuery.data?.length ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalCategorias / PAGE_SIZE));
  const canGoNext = page < totalPages;

  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages);
    }
  }, [page, totalPages]);

  function handleSearchSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPage(1);
    setCurrentSearch(search);
  }

  function clearFilters() {
    setSearch("");
    setCurrentSearch("");
    setSoloRaiz(false);
    setIncluirEliminadas(false);
    setPage(1);
  }

  function handleNew() {
    if (!canManage) return;
    setSelected(null);
    setFormError(null);
    setDefaultParentId(null);
    setOpen(true);
  }

  function handleNewChild(categoria: Categoria) {
    if (!canManage) return;
    setSelected(null);
    setDefaultParentId(categoria.id);
    setFormError(null);
    setOpen(true);
  }

  function handleEdit(categoria: Categoria) {
    if (!canManage) return;
    setSelected(categoria);
    setDefaultParentId(null);
    setFormError(null);
    setOpen(true);
  }

  function handleClose() {
    if (crearMutation.isPending || actualizarMutation.isPending) {
      return;
    }

    setOpen(false);
    setSelected(null);
    setDefaultParentId(null);
    setFormError(null);
  }

  async function handleSubmit(payload: CategoriaPayload) {
    try {
      if (selected) {
        await actualizarMutation.mutateAsync({ id: selected.id, payload });
      } else {
        await crearMutation.mutateAsync(payload);
      }
      handleClose();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Ocurrió un error al guardar.");
    }
  }

  async function handleDelete(categoria: Categoria) {
    if (!canManage || deleting) return;

    const confirmacion = window.confirm(
      `¿Seguro que querés eliminar la categoría "${categoria.nombre}"?`
    );

    if (!confirmacion) return;

    try {
      await eliminarMutation.mutateAsync(categoria.id);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo eliminar.");
    }
  }

  async function handleActivate(categoria: Categoria) {
    if (!canManage) return;
    try {
      await activarMutation.mutateAsync(categoria.id);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo activar la categoría.");
    }
  }

  async function handleExport() {
    setExportando(true);
    try {
      await descargarExcel("categorias", true);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo exportar a Excel.");
    } finally {
      setExportando(false);
    }
  }

  return (
    <PageContainer
      title="Categorías"
      subtitle="ABM de categorías jerárquicas con vista árbol, búsqueda y filtros de administración."
      actions={
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={handleExport}
            disabled={exportando}
            className="rounded-2xl border border-emerald-400/30 bg-emerald-500/10 px-4 py-3 font-semibold text-emerald-100 hover:bg-emerald-500/20 disabled:opacity-60"
          >
            {exportando ? "Exportando..." : "Exportar Excel"}
          </button>
          {canManage ? <button
            type="button"
            onClick={handleNew}
            disabled={deleting}
            className="rounded-2xl bg-blue-500 px-4 py-3 font-semibold text-white hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Nueva categoría
          </button> : null}
        </div>
      }
    >
      <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <form className="grid gap-3 lg:grid-cols-[1fr_auto_auto]" onSubmit={handleSearchSubmit}>
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Buscar por nombre o descripción"
            className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500"
          />
          <button type="submit" disabled={categoriasQuery.isFetching} className="rounded-2xl border border-white/10 px-4 py-3 font-semibold text-slate-100 hover:bg-white/10 disabled:opacity-60">
            Buscar
          </button>
          <button type="button" onClick={clearFilters} className="rounded-2xl border border-white/10 px-4 py-3 font-semibold text-slate-100 hover:bg-white/10">
            Limpiar
          </button>
        </form>

        <div className="mt-4 flex flex-wrap gap-4">
          <label className="flex items-center gap-2 text-sm text-slate-300">
            <input
              type="checkbox"
              checked={soloRaiz}
              onChange={(event) => { setSoloRaiz(event.target.checked); setPage(1); }}
            />
            Mostrar solo categorías raíz
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-300">
            <input
              type="checkbox"
              checked={incluirEliminadas}
              onChange={(event) => { setIncluirEliminadas(event.target.checked); setPage(1); }}
            />
            Ver categorías eliminadas
          </label>
        </div>
      </div>

      {categoriasQuery.isLoading ? (
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-slate-300">
          Cargando categorías...
        </div>
      ) : null}

      {categoriasQuery.isError ? (
        <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-rose-200">
          {categoriasQuery.error instanceof Error
            ? categoriasQuery.error.message
            : "Ocurrió un error al cargar las categorías."}
        </div>
      ) : null}

      {categoriasQuery.data ? (
        <CategoriaTable
          items={categoriasQuery.data}
          canManage={canManage}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onCreateChild={handleNewChild}
          onActivate={handleActivate}
          page={page}
          pageSize={PAGE_SIZE}
        />
      ) : null}

      <div className="flex items-center justify-between rounded-3xl border border-white/10 bg-white/5 px-5 py-4">
        <button type="button" onClick={() => setPage((current) => Math.max(1, current - 1))} disabled={page === 1 || categoriasQuery.isFetching} className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10 disabled:opacity-50">Página anterior</button>
        <p className="text-sm text-slate-300">Página {page} de {totalPages}{categoriasQuery.isFetching ? " · actualizando..." : ""}</p>
        <button type="button" onClick={() => setPage((current) => current + 1)} disabled={!canGoNext || categoriasQuery.isFetching} className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10 disabled:opacity-50">Página siguiente</button>
      </div>

      <CategoriaModal
        open={open}
        initialData={selected}
        categorias={categoriasQuery.data ?? []}
        defaultParentId={defaultParentId}
        saving={crearMutation.isPending || actualizarMutation.isPending}
        error={formError}
        onClose={handleClose}
        onSubmit={handleSubmit}
      />
    </PageContainer>
  );
}
