import { useMemo, useState } from "react";

import IngredienteModal from "../components/ingredientes/IngredienteModal";
import IngredienteTable from "../components/ingredientes/IngredienteTable";
import PageContainer from "../components/layout/PageContainer";
import { useAuth } from "../hooks/useAuth";
import { useUnidadesMedida } from "../hooks/useUnidadesMedida";
import {
  useActualizarIngrediente,
  useActivarIngrediente,
  useCrearIngrediente,
  useEliminarIngrediente,
  useIngredientes,
} from "../hooks/useIngredientes";
import { descargarExcel } from "../services/exportService";
import type { Ingrediente, IngredientePayload } from "../types/ingrediente";

const PAGE_SIZE = 10;

export default function IngredientesPage() {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<Ingrediente | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [incluirEliminados, setIncluirEliminados] = useState(false);
  const [exportando, setExportando] = useState(false);

  const { hasRole } = useAuth();
  const canManage = hasRole("ADMIN");

  const ingredientesQuery = useIngredientes({ page, size: PAGE_SIZE, incluir_eliminados: incluirEliminados });
  const unidadesQuery = useUnidadesMedida();
  const crearMutation = useCrearIngrediente();
  const actualizarMutation = useActualizarIngrediente();
  const eliminarMutation = useEliminarIngrediente();
  const activarMutation = useActivarIngrediente();
  const deleting = eliminarMutation.isPending;
  const canGoNext = useMemo(() => (ingredientesQuery.data?.length ?? 0) === PAGE_SIZE, [ingredientesQuery.data]);

  function handleNew() {
    if (!canManage) return;
    setSelected(null);
    setFormError(null);
    setOpen(true);
  }

  function handleEdit(ingrediente: Ingrediente) {
    if (!canManage) return;
    setSelected(ingrediente);
    setFormError(null);
    setOpen(true);
  }

  function handleClose() {
    if (crearMutation.isPending || actualizarMutation.isPending) {
      return;
    }

    setOpen(false);
    setSelected(null);
    setFormError(null);
  }

  async function handleSubmit(payload: IngredientePayload) {
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

  async function handleDelete(ingrediente: Ingrediente) {
    if (!canManage || deleting) return;

    const confirmacion = window.confirm(
      `¿Seguro que querés eliminar el ingrediente "${ingrediente.nombre}"?`
    );

    if (!confirmacion) return;

    try {
      await eliminarMutation.mutateAsync(ingrediente.id);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo eliminar.");
    }
  }


  async function handleActivate(ingrediente: Ingrediente) {
    if (!canManage) return;
    try {
      await activarMutation.mutateAsync(ingrediente.id);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo activar el ingrediente.");
    }
  }

  async function handleExport() {
    setExportando(true);
    try {
      await descargarExcel("ingredientes", true);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo exportar a Excel.");
    } finally {
      setExportando(false);
    }
  }

  return (
    <PageContainer
      title="Ingredientes"
      subtitle="ABM de ingredientes con tabla, acciones y modal tipado en TypeScript."
      actions={
        <div className="flex flex-wrap gap-2">
          <button type="button" onClick={handleExport} disabled={exportando} className="rounded-2xl border border-emerald-400/30 bg-emerald-500/10 px-4 py-3 font-semibold text-emerald-100 hover:bg-emerald-500/20 disabled:opacity-60">{exportando ? "Exportando..." : "Exportar Excel"}</button>
          {canManage ? <button
            type="button"
            onClick={handleNew}
            disabled={deleting}
            className="rounded-2xl bg-blue-500 px-4 py-3 font-semibold text-white hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Nuevo ingrediente
          </button> : null}
        </div>
      }
    >
      <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <label className="flex items-center gap-2 text-sm text-slate-300">
          <input type="checkbox" checked={incluirEliminados} onChange={(event) => { setIncluirEliminados(event.target.checked); setPage(1); }} />
          Ver ingredientes eliminados
        </label>
      </div>

      {ingredientesQuery.isLoading ? (
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-slate-300">
          Cargando ingredientes...
        </div>
      ) : null}

      {ingredientesQuery.isError ? (
        <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-rose-200">
          {ingredientesQuery.error instanceof Error
            ? ingredientesQuery.error.message
            : "Ocurrió un error al cargar los ingredientes."}
        </div>
      ) : null}

      {ingredientesQuery.data ? (
        <IngredienteTable
          items={ingredientesQuery.data}
          canManage={canManage}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onActivate={handleActivate}
        />
      ) : null}

      <div className="flex items-center justify-between rounded-3xl border border-white/10 bg-white/5 px-5 py-4">
        <button type="button" onClick={() => setPage((current) => Math.max(1, current - 1))} disabled={page === 1 || ingredientesQuery.isFetching} className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10 disabled:opacity-50">Página anterior</button>
        <p className="text-sm text-slate-300">Página {page}{ingredientesQuery.isFetching ? " · actualizando..." : ""}</p>
        <button type="button" onClick={() => setPage((current) => current + 1)} disabled={!canGoNext || ingredientesQuery.isFetching} className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10 disabled:opacity-50">Página siguiente</button>
      </div>

      <IngredienteModal
        open={open}
        initialData={selected}
        unidadesMedida={unidadesQuery.data ?? []}
        saving={crearMutation.isPending || actualizarMutation.isPending}
        error={formError}
        onClose={handleClose}
        onSubmit={handleSubmit}
      />
    </PageContainer>
  );
}
