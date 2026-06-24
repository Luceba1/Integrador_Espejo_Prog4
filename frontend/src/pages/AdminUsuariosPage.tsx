import { useMemo, useState } from "react";

import Modal from "../components/common/Modal";
import PageContainer from "../components/layout/PageContainer";
import {
  useActualizarRolesUsuario,
  useActivarUsuario,
  useActualizarUsuario,
  useEliminarUsuario,
  useRoles,
  useUsuariosAdmin,
} from "../hooks/useAdminUsuarios";
import { descargarExcel } from "../services/exportService";
import type { UsuarioAdmin } from "../types/admin";

const PAGE_SIZE = 10;

export default function AdminUsuariosPage() {
  const [search, setSearch] = useState("");
  const [currentSearch, setCurrentSearch] = useState("");
  const [rol, setRol] = useState("");
  const [page, setPage] = useState(1);
  const [incluirEliminados, setIncluirEliminados] = useState(false);
  const [exportando, setExportando] = useState(false);

  const [editing, setEditing] = useState<UsuarioAdmin | null>(null);
  const [editNombre, setEditNombre] = useState("");
  const [editApellido, setEditApellido] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const usuariosQuery = useUsuariosAdmin({
    search: currentSearch || undefined,
    rol: rol || undefined,
    page,
    size: PAGE_SIZE,
    incluir_eliminados: incluirEliminados,
  });
  const rolesQuery = useRoles();
  const actualizarUsuario = useActualizarUsuario();
  const actualizarRoles = useActualizarRolesUsuario();
  const eliminarUsuario = useEliminarUsuario();
  const activarUsuario = useActivarUsuario();

  const canGoNext = useMemo(() => (usuariosQuery.data?.length ?? 0) === PAGE_SIZE, [usuariosQuery.data]);
  const isSaving = actualizarUsuario.isPending;

  function handleSearch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPage(1);
    setCurrentSearch(search);
  }

  function startEdit(usuario: UsuarioAdmin) {
    setEditing(usuario);
    setEditNombre(usuario.nombre ?? "");
    setEditApellido(usuario.apellido ?? "");
    setEditEmail(usuario.email ?? "");
    setFormError(null);
  }

  function closeEdit() {
    if (isSaving) return;
    setEditing(null);
    setEditNombre("");
    setEditApellido("");
    setEditEmail("");
    setFormError(null);
  }

  async function handleEditSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!editing) return;

    const payload = {
      nombre: editNombre.trim(),
      apellido: editApellido.trim() || null,
      email: editEmail.trim(),
    };

    if (!payload.nombre || !payload.email) {
      setFormError("Completá nombre y email.");
      return;
    }

    try {
      await actualizarUsuario.mutateAsync({ id: editing.id, payload });
      closeEdit();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "No se pudo editar el usuario.");
    }
  }

  async function handleActivate(usuario: UsuarioAdmin) {
    try {
      await activarUsuario.mutateAsync(usuario.id);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo activar el usuario.");
    }
  }

  async function toggleRol(usuario: UsuarioAdmin, rolCodigo: string) {
    if (usuario.deleted_at) {
      window.alert("Primero activá el usuario para modificar sus roles.");
      return;
    }

    const currentRoles = usuario.roles.map((item) => item.codigo);
    const nextRoles = currentRoles.includes(rolCodigo)
      ? currentRoles.filter((item) => item !== rolCodigo)
      : [...currentRoles, rolCodigo];

    if (!nextRoles.length) {
      window.alert("El usuario debe tener al menos un rol.");
      return;
    }

    try {
      await actualizarRoles.mutateAsync({ id: usuario.id, roles: nextRoles });
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudieron actualizar los roles.");
    }
  }

  async function handleDelete(usuario: UsuarioAdmin) {
    const ok = window.confirm(`¿Seguro que querés eliminar a ${usuario.email}?`);
    if (!ok) return;

    try {
      await eliminarUsuario.mutateAsync(usuario.id);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo eliminar el usuario.");
    }
  }

  async function handleExport() {
    setExportando(true);
    try {
      await descargarExcel("usuarios", true);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo exportar a Excel.");
    } finally {
      setExportando(false);
    }
  }

  return (
    <PageContainer
      title="Usuarios"
      subtitle="Gestión administrativa: listado paginado, filtro por rol, baja lógica, reactivación, edición y asignación de roles."
      actions={
        <button type="button" onClick={handleExport} disabled={exportando} className="rounded-2xl border border-emerald-400/30 bg-emerald-500/10 px-4 py-3 font-semibold text-emerald-100 hover:bg-emerald-500/20 disabled:opacity-60">
          {exportando ? "Exportando..." : "Exportar Excel"}
        </button>
      }
    >
      <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <form className="grid gap-3 md:grid-cols-[1fr_220px_auto]" onSubmit={handleSearch}>
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar por nombre o email" className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500" />
          <select value={rol} onChange={(event) => { setRol(event.target.value); setPage(1); }} className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none">
            <option value="">Todos los roles</option>
            {(rolesQuery.data ?? []).map((item) => <option key={item.codigo} value={item.codigo}>{item.codigo}</option>)}
          </select>
          <button type="submit" className="rounded-2xl border border-white/10 px-4 py-3 font-semibold text-slate-100 hover:bg-white/10">Buscar</button>
        </form>
        <label className="mt-3 flex items-center gap-2 text-sm text-slate-300">
          <input type="checkbox" checked={incluirEliminados} onChange={(event) => { setIncluirEliminados(event.target.checked); setPage(1); }} />
          Ver usuarios eliminados
        </label>
      </div>

      {usuariosQuery.isLoading ? <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-slate-300">Cargando usuarios...</div> : null}
      {usuariosQuery.isError ? <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-rose-200">{usuariosQuery.error instanceof Error ? usuariosQuery.error.message : "No se pudieron cargar los usuarios."}</div> : null}

      {usuariosQuery.data ? (
        <div className="overflow-hidden rounded-3xl border border-white/10 bg-slate-900/70">
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-white/5 text-slate-300">
                <tr>
                  <th className="px-5 py-4">Usuario</th>
                  <th className="px-5 py-4">Estado</th>
                  <th className="px-5 py-4">Roles</th>
                  <th className="px-5 py-4 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {usuariosQuery.data.map((usuario) => (
                  <tr key={usuario.id} className={`border-t border-white/5 align-top transition ${usuario.deleted_at ? "bg-slate-950/70 text-slate-500" : ""}`}>
                    <td className="px-5 py-4">
                      <p className="font-semibold text-white">{usuario.nombre} {usuario.apellido ?? ""}</p>
                      <p className="mt-1 text-xs text-slate-400">{usuario.email}</p>
                    </td>
                    <td className="px-5 py-4">
                      <span className={[
                        "rounded-full px-3 py-1 text-xs font-semibold",
                        usuario.deleted_at ? "bg-rose-500/15 text-rose-200" : "bg-emerald-500/15 text-emerald-200",
                      ].join(" ")}>{usuario.deleted_at ? "Eliminado" : "Activo"}</span>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex flex-wrap gap-2">
                        {(rolesQuery.data ?? []).map((item) => {
                          const checked = usuario.roles.some((rolItem) => rolItem.codigo === item.codigo);
                          return (
                            <button key={item.codigo} type="button" onClick={() => toggleRol(usuario, item.codigo)} disabled={actualizarRoles.isPending || Boolean(usuario.deleted_at)} className={[
                              "rounded-full px-3 py-1 text-xs font-semibold transition disabled:opacity-50",
                              checked ? "bg-sky-500/20 text-sky-200" : "bg-white/5 text-slate-400 hover:bg-white/10",
                            ].join(" ")}>{item.codigo}</button>
                          );
                        })}
                      </div>
                    </td>
                    <td className="px-5 py-4 text-right">
                      <div className="flex justify-end gap-2">
                        {usuario.deleted_at ? <button type="button" onClick={() => handleActivate(usuario)} disabled={activarUsuario.isPending} className="rounded-xl bg-emerald-500 px-3 py-2 font-semibold text-white shadow-lg shadow-emerald-500/20 hover:bg-emerald-400 disabled:opacity-60">Activar</button> : null}
                        <button type="button" onClick={() => startEdit(usuario)} disabled={Boolean(usuario.deleted_at)} className={usuario.deleted_at ? "cursor-not-allowed rounded-xl bg-slate-800 px-3 py-2 font-medium text-slate-500" : "rounded-xl bg-amber-500/15 px-3 py-2 font-medium text-amber-200 hover:bg-amber-500/25 disabled:opacity-60"}>Editar</button>
                        <button type="button" onClick={() => handleDelete(usuario)} disabled={eliminarUsuario.isPending || Boolean(usuario.deleted_at)} className={usuario.deleted_at ? "cursor-not-allowed rounded-xl bg-slate-800 px-3 py-2 font-medium text-slate-500" : "rounded-xl bg-rose-500/15 px-3 py-2 font-medium text-rose-200 hover:bg-rose-500/25 disabled:opacity-60"}>Eliminar</button>
                      </div>
                    </td>
                  </tr>
                ))}
                {!usuariosQuery.data.length ? <tr><td colSpan={4} className="px-5 py-10 text-center text-slate-400">No hay usuarios para mostrar.</td></tr> : null}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}

      <div className="flex items-center justify-between rounded-3xl border border-white/10 bg-white/5 px-5 py-4">
        <button type="button" onClick={() => setPage((current) => Math.max(1, current - 1))} disabled={page === 1 || usuariosQuery.isFetching} className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10 disabled:opacity-50">Página anterior</button>
        <p className="text-sm text-slate-300">Página {page}{usuariosQuery.isFetching ? " · actualizando..." : ""}</p>
        <button type="button" onClick={() => setPage((current) => current + 1)} disabled={!canGoNext || usuariosQuery.isFetching} className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10 disabled:opacity-50">Página siguiente</button>
      </div>

      <Modal open={Boolean(editing)} title="Editar usuario" onClose={closeEdit}>
        <form onSubmit={handleEditSubmit} className="space-y-4">
          {formError ? <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{formError}</div> : null}
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-200">Nombre</label>
              <input value={editNombre} onChange={(event) => setEditNombre(event.target.value)} className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none" required />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-200">Apellido</label>
              <input value={editApellido} onChange={(event) => setEditApellido(event.target.value)} className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none" />
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-200">Email</label>
            <input type="email" value={editEmail} onChange={(event) => setEditEmail(event.target.value)} className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none" required />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button type="button" onClick={closeEdit} className="rounded-2xl border border-white/10 px-4 py-3 font-semibold text-slate-200 hover:bg-white/10">Cancelar</button>
            <button type="submit" disabled={isSaving} className="rounded-2xl bg-blue-500 px-4 py-3 font-semibold text-white hover:bg-blue-400 disabled:opacity-60">{isSaving ? "Guardando..." : "Guardar cambios"}</button>
          </div>
        </form>
      </Modal>
    </PageContainer>
  );
}
