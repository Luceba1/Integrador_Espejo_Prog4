import { useMemo, useState } from "react";

import Modal from "../components/common/Modal";
import PageContainer from "../components/layout/PageContainer";
import {
  useActualizarUnidadMedida,
  useActivarUnidadMedida,
  useCrearUnidadMedida,
  useEliminarUnidadMedida,
  useUnidadesMedida,
} from "../hooks/useUnidadesMedida";
import { descargarExcel } from "../services/exportService";
import type { UnidadMedida } from "../types/unidadMedida";

const TIPOS = ["contable", "peso", "volumen", "otros"];
const PAGE_SIZE = 10;

export default function UnidadesMedidaPage() {
  const [page, setPage] = useState(1);
  const [incluirEliminadas, setIncluirEliminadas] = useState(false);
  const [search, setSearch] = useState("");
  const [currentSearch, setCurrentSearch] = useState("");
  const [tipoFilter, setTipoFilter] = useState("");
  const [exportando, setExportando] = useState(false);
  const [openForm, setOpenForm] = useState(false);

  const unidadesQuery = useUnidadesMedida({
    page,
    size: PAGE_SIZE,
    incluir_eliminadas: incluirEliminadas,
    search: currentSearch,
    tipo: tipoFilter || undefined,
  });
  const crearMutation = useCrearUnidadMedida();
  const actualizarMutation = useActualizarUnidadMedida();
  const eliminarMutation = useEliminarUnidadMedida();
  const activarMutation = useActivarUnidadMedida();

  const [editing, setEditing] = useState<UnidadMedida | null>(null);
  const [nombre, setNombre] = useState("");
  const [simbolo, setSimbolo] = useState("");
  const [tipo, setTipo] = useState("contable");
  const [formError, setFormError] = useState<string | null>(null);

  const isSaving = crearMutation.isPending || actualizarMutation.isPending;
  const canGoNext = useMemo(() => (unidadesQuery.data?.length ?? 0) === PAGE_SIZE, [unidadesQuery.data]);

  function handleSearchSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPage(1);
    setCurrentSearch(search);
  }

  function clearFilters() {
    setSearch("");
    setCurrentSearch("");
    setTipoFilter("");
    setIncluirEliminadas(false);
    setPage(1);
  }

  function resetForm() {
    setEditing(null);
    setNombre("");
    setSimbolo("");
    setTipo("contable");
    setFormError(null);
  }

  function handleNew() {
    resetForm();
    setOpenForm(true);
  }

  function closeForm() {
    if (isSaving) return;
    resetForm();
    setOpenForm(false);
  }

  function startEdit(unidad: UnidadMedida) {
    setEditing(unidad);
    setNombre(unidad.nombre);
    setSimbolo(unidad.simbolo);
    setTipo(unidad.tipo);
    setFormError(null);
    setOpenForm(true);
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);

    const payload = {
      nombre: nombre.trim(),
      simbolo: simbolo.trim(),
      tipo: tipo.trim(),
      activo: true,
    };

    if (!payload.nombre || !payload.simbolo || !payload.tipo) {
      setFormError("Completá nombre, símbolo y tipo.");
      return;
    }

    try {
      if (editing) {
        await actualizarMutation.mutateAsync({ id: editing.id, payload });
      } else {
        await crearMutation.mutateAsync(payload);
      }
      closeForm();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "No se pudo guardar la unidad de medida.");
    }
  }

  async function handleDelete(unidad: UnidadMedida) {
    const ok = window.confirm(`¿Seguro que querés eliminar la unidad "${unidad.nombre}"?`);
    if (!ok) return;

    try {
      await eliminarMutation.mutateAsync(unidad.id);
      if (editing?.id === unidad.id) closeForm();
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo eliminar la unidad de medida.");
    }
  }

  async function handleActivate(unidad: UnidadMedida) {
    try {
      await activarMutation.mutateAsync(unidad.id);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo activar la unidad de medida.");
    }
  }

  async function handleExport() {
    setExportando(true);
    try {
      await descargarExcel("unidades-medida", true);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo exportar a Excel.");
    } finally {
      setExportando(false);
    }
  }

  return (
    <PageContainer
      title="Unidades de medida"
      subtitle="Catálogo v7 con búsqueda y filtros para administrar unidades de medida."
      actions={
        <div className="flex flex-wrap gap-2">
          <button type="button" onClick={handleExport} disabled={exportando} className="rounded-2xl border border-emerald-400/30 bg-emerald-500/10 px-4 py-3 font-semibold text-emerald-100 hover:bg-emerald-500/20 disabled:opacity-60">
            {exportando ? "Exportando..." : "Exportar Excel"}
          </button>
          <button type="button" onClick={handleNew} className="rounded-2xl bg-blue-500 px-4 py-3 font-semibold text-white hover:bg-blue-400">
            Nueva unidad
          </button>
        </div>
      }
    >
      <div className="space-y-4">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
          <form className="grid gap-3 lg:grid-cols-[1fr_180px_auto_auto]" onSubmit={handleSearchSubmit}>
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Buscar por nombre o símbolo"
              className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500"
            />
            <select
              value={tipoFilter}
              onChange={(event) => { setTipoFilter(event.target.value); setPage(1); }}
              className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
            >
              <option value="">Todos los tipos</option>
              {TIPOS.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
            <button type="submit" disabled={unidadesQuery.isFetching} className="rounded-2xl border border-white/10 px-4 py-3 font-semibold text-slate-100 hover:bg-white/10 disabled:opacity-60">
              Buscar
            </button>
            <button type="button" onClick={clearFilters} className="rounded-2xl border border-white/10 px-4 py-3 font-semibold text-slate-100 hover:bg-white/10">
              Limpiar
            </button>
          </form>
          <label className="mt-4 flex items-center gap-2 text-sm text-slate-300">
            <input type="checkbox" checked={incluirEliminadas} onChange={(event) => { setIncluirEliminadas(event.target.checked); setPage(1); }} />
            Ver unidades eliminadas
          </label>
        </div>

        <div className="overflow-hidden rounded-3xl border border-white/10 bg-slate-900/70">
          {unidadesQuery.isLoading ? <div className="p-8 text-slate-300">Cargando unidades...</div> : null}
          {unidadesQuery.isError ? <div className="p-8 text-rose-200">{unidadesQuery.error instanceof Error ? unidadesQuery.error.message : "No se pudieron cargar las unidades."}</div> : null}

          {unidadesQuery.data ? (
            <div className="overflow-x-auto">
              <table className="min-w-full text-left text-sm">
                <thead className="bg-white/5 text-slate-300">
                  <tr>
                    <th className="px-5 py-4">Nombre</th>
                    <th className="px-5 py-4">Símbolo</th>
                    <th className="px-5 py-4">Tipo</th>
                    <th className="px-5 py-4">Estado</th>
                    <th className="px-5 py-4 text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {unidadesQuery.data.map((unidad) => (
                    <tr key={unidad.id} className={`border-t border-white/5 transition ${unidad.deleted_at ? "bg-slate-950/70 text-slate-500" : ""}`}>
                      <td className="px-5 py-4 font-semibold text-white">{unidad.nombre}</td>
                      <td className="px-5 py-4 text-slate-300">{unidad.simbolo}</td>
                      <td className="px-5 py-4"><span className="rounded-full bg-sky-500/15 px-3 py-1 text-xs font-semibold text-sky-200">{unidad.tipo}</span></td>
                      <td className="px-5 py-4">{unidad.deleted_at ? <span className="rounded-full bg-rose-500/15 px-3 py-1 text-xs font-semibold text-rose-200">Eliminada</span> : <span className="rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-semibold text-emerald-200">Activa</span>}</td>
                      <td className="px-5 py-4">
                        <div className="flex justify-end gap-2">
                          {unidad.deleted_at ? <button type="button" onClick={() => handleActivate(unidad)} disabled={activarMutation.isPending} className="rounded-xl bg-emerald-500 px-3 py-2 font-semibold text-white shadow-lg shadow-emerald-500/20 hover:bg-emerald-400 disabled:opacity-60">Activar</button> : null}
                          <button type="button" onClick={() => startEdit(unidad)} disabled={Boolean(unidad.deleted_at)} className={unidad.deleted_at ? "cursor-not-allowed rounded-xl bg-slate-800 px-3 py-2 font-medium text-slate-500" : "rounded-xl bg-amber-500/15 px-3 py-2 font-medium text-amber-200 hover:bg-amber-500/25 disabled:opacity-60"}>Editar</button>
                          <button type="button" onClick={() => handleDelete(unidad)} disabled={eliminarMutation.isPending || Boolean(unidad.deleted_at)} className={unidad.deleted_at ? "cursor-not-allowed rounded-xl bg-slate-800 px-3 py-2 font-medium text-slate-500" : "rounded-xl bg-rose-500/15 px-3 py-2 font-medium text-rose-200 hover:bg-rose-500/25 disabled:opacity-60"}>Eliminar</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {!unidadesQuery.data.length ? <tr><td colSpan={5} className="px-5 py-10 text-center text-slate-400">No hay unidades cargadas.</td></tr> : null}
                </tbody>
              </table>
            </div>
          ) : null}
        </div>

        <div className="flex items-center justify-between rounded-3xl border border-white/10 bg-white/5 px-5 py-4">
          <button type="button" onClick={() => setPage((current) => Math.max(1, current - 1))} disabled={page === 1 || unidadesQuery.isFetching} className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10 disabled:opacity-50">Página anterior</button>
          <p className="text-sm text-slate-300">Página {page}{unidadesQuery.isFetching ? " · actualizando..." : ""}</p>
          <button type="button" onClick={() => setPage((current) => current + 1)} disabled={!canGoNext || unidadesQuery.isFetching} className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10 disabled:opacity-50">Página siguiente</button>
        </div>
      </div>

      <Modal open={openForm} title={editing ? "Editar unidad" : "Nueva unidad"} onClose={closeForm}>
        <form onSubmit={handleSubmit} className="space-y-4">
          {formError ? <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{formError}</div> : null}

          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-200">Nombre</label>
            <input value={nombre} onChange={(event) => setNombre(event.target.value)} placeholder="Kilogramo" className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500" minLength={2} maxLength={50} required />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-200">Símbolo</label>
            <input value={simbolo} onChange={(event) => setSimbolo(event.target.value)} placeholder="kg" className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500" minLength={1} maxLength={10} required />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-200">Tipo</label>
            <select value={tipo} onChange={(event) => setTipo(event.target.value)} className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none">
              {TIPOS.map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={closeForm} className="rounded-2xl border border-white/10 px-4 py-3 font-semibold text-slate-200 hover:bg-white/10">Cancelar</button>
            <button type="submit" disabled={isSaving} className="rounded-2xl bg-blue-500 px-4 py-3 font-semibold text-white hover:bg-blue-400 disabled:opacity-60">
              {isSaving ? "Guardando..." : editing ? "Actualizar" : "Crear"}
            </button>
          </div>
        </form>
      </Modal>
    </PageContainer>
  );
}
