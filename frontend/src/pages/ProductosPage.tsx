import { useMemo, useState } from "react";

import PageContainer from "../components/layout/PageContainer";
import ProductoModal from "../components/productos/ProductoModal";
import ProductoTable from "../components/productos/ProductoTable";
import { useCategorias } from "../hooks/useCategorias";
import { useIngredientes } from "../hooks/useIngredientes";
import { useUnidadesMedida } from "../hooks/useUnidadesMedida";
import {
  useActualizarProducto,
  useActualizarStockProducto,
  useActivarProducto,
  useCambiarDisponibilidadProducto,
  useCrearProducto,
  useEliminarProducto,
  useProductos,
} from "../hooks/useProductos";
import { useAuth } from "../hooks/useAuth";
import { descargarExcel } from "../services/exportService";
import type { Producto, ProductoPayload } from "../types/producto";

const PAGE_SIZE = 10;

export default function ProductosPage() {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<Producto | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [currentSearch, setCurrentSearch] = useState("");
  const [page, setPage] = useState(1);
  const [incluirEliminados, setIncluirEliminados] = useState(false);
  const [disponibilidadFilter, setDisponibilidadFilter] = useState("todos");
  const [categoriaFilter, setCategoriaFilter] = useState("");
  const [exportando, setExportando] = useState(false);

  const { hasRole } = useAuth();
  const canManage = hasRole("ADMIN");
  const canManageStock = hasRole("ADMIN", "STOCK");

  const categoriasQuery = useCategorias();
  const ingredientesQuery = useIngredientes();
  const unidadesQuery = useUnidadesMedida();
  const productosQuery = useProductos(currentSearch, page, PAGE_SIZE, {
    incluir_eliminados: incluirEliminados,
    disponible: disponibilidadFilter === "todos" ? undefined : disponibilidadFilter === "disponibles",
    categoria_id: categoriaFilter ? Number(categoriaFilter) : undefined,
  });

  const crearMutation = useCrearProducto();
  const actualizarMutation = useActualizarProducto();
  const eliminarMutation = useEliminarProducto();
  const disponibilidadMutation = useCambiarDisponibilidadProducto();
  const stockMutation = useActualizarStockProducto();
  const activarMutation = useActivarProducto();

  const isSaving = crearMutation.isPending || actualizarMutation.isPending;
  const isDeleting = eliminarMutation.isPending;
  const isChangingAvailability = disponibilidadMutation.isPending;
  const isChangingStock = stockMutation.isPending;

  const canGoNext = useMemo(() => {
    return (productosQuery.data?.length ?? 0) === PAGE_SIZE;
  }, [productosQuery.data]);

  function handleSearchSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPage(1);
    setCurrentSearch(search);
  }

  function clearFilters() {
    setSearch("");
    setCurrentSearch("");
    setDisponibilidadFilter("todos");
    setCategoriaFilter("");
    setIncluirEliminados(false);
    setPage(1);
  }

  function handleNew() {
    if (!canManage) return;
    setSelected(null);
    setFormError(null);
    setOpen(true);
  }

  function handleEdit(producto: Producto) {
    if (!canManage) return;
    setSelected(producto);
    setFormError(null);
    setOpen(true);
  }

  function handleClose() {
    if (isSaving) {
      return;
    }

    setOpen(false);
    setSelected(null);
    setFormError(null);
  }

  async function handleSubmit(payload: ProductoPayload) {
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

  async function handleDelete(producto: Producto) {
    if (!canManage || isDeleting) return;

    const confirmacion = window.confirm(
      `¿Seguro que querés eliminar el producto "${producto.nombre}"?`
    );

    if (!confirmacion) return;

    try {
      await eliminarMutation.mutateAsync(producto.id);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo eliminar.");
    }
  }


  async function handleActivate(producto: Producto) {
    if (!canManage) return;
    try {
      await activarMutation.mutateAsync(producto.id);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo activar el producto.");
    }
  }

  async function handleExport() {
    setExportando(true);
    try {
      await descargarExcel("productos", true);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo exportar a Excel.");
    } finally {
      setExportando(false);
    }
  }

  async function handleToggleDisponibilidad(producto: Producto) {
    if (!canManageStock || isChangingAvailability) return;

    try {
      await disponibilidadMutation.mutateAsync({ id: producto.id, disponible: !producto.disponible });
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo cambiar la disponibilidad.");
    }
  }

  async function handleUpdateStock(producto: Producto) {
    if (!canManageStock || isChangingStock) return;

    const value = window.prompt(`Nuevo stock para "${producto.nombre}"`, String(producto.stock_cantidad));
    if (value === null) return;

    const stock = Number(value);
    if (!Number.isInteger(stock) || stock < 0) {
      window.alert("El stock debe ser un número entero mayor o igual a 0.");
      return;
    }

    try {
      await stockMutation.mutateAsync({ id: producto.id, stock_cantidad: stock });
    } catch (error) {
      window.alert(error instanceof Error ? error.message : "No se pudo actualizar el stock.");
    }
  }


  return (
    <PageContainer
      title="Productos"
      subtitle="Listado con búsqueda, paginación simple, detalle, categorías e ingredientes relacionados."
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
            disabled={isDeleting || categoriasQuery.isLoading || ingredientesQuery.isLoading || unidadesQuery.isLoading}
            className="rounded-2xl bg-blue-500 px-4 py-3 font-semibold text-white hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Nuevo producto
          </button> : null}
        </div>
      }
    >
      <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <form className="grid gap-3 xl:grid-cols-[1fr_190px_220px_auto_auto]" onSubmit={handleSearchSubmit}>
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Buscar por nombre o descripción"
            className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500"
          />
          <select
            value={disponibilidadFilter}
            onChange={(event) => { setDisponibilidadFilter(event.target.value); setPage(1); }}
            className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
          >
            <option value="todos">Todos</option>
            <option value="disponibles">Disponibles</option>
            <option value="no_disponibles">No disponibles</option>
          </select>
          <select
            value={categoriaFilter}
            onChange={(event) => { setCategoriaFilter(event.target.value); setPage(1); }}
            className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
          >
            <option value="">Todas las categorías</option>
            {(categoriasQuery.data ?? []).map((categoria) => (
              <option key={categoria.id} value={categoria.id}>{categoria.nombre}</option>
            ))}
          </select>
          <button
            type="submit"
            disabled={productosQuery.isFetching}
            className="rounded-2xl border border-white/10 px-4 py-3 font-semibold text-slate-100 hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Buscar
          </button>
          <button type="button" onClick={clearFilters} className="rounded-2xl border border-white/10 px-4 py-3 font-semibold text-slate-100 hover:bg-white/10">
            Limpiar
          </button>
        </form>
        <label className="mt-3 flex items-center gap-2 text-sm text-slate-300">
          <input
            type="checkbox"
            checked={incluirEliminados}
            onChange={(event) => { setIncluirEliminados(event.target.checked); setPage(1); }}
          />
          Ver productos eliminados
        </label>
      </div>

      {productosQuery.isLoading ? (
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-slate-300">
          Cargando productos...
        </div>
      ) : null}

      {productosQuery.isError ? (
        <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-rose-200">
          {productosQuery.error instanceof Error
            ? productosQuery.error.message
            : "Ocurrió un error al cargar los productos."}
        </div>
      ) : null}

      {productosQuery.data ? (
        <>
          <ProductoTable
            items={productosQuery.data}
            canManage={canManage}
            canManageStock={canManageStock}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onToggleDisponibilidad={handleToggleDisponibilidad}
            onUpdateStock={handleUpdateStock}
            onActivate={handleActivate}
          />

          <div className="flex items-center justify-between rounded-3xl border border-white/10 bg-white/5 px-5 py-4">
            <button
              type="button"
              onClick={() => setPage((current) => Math.max(1, current - 1))}
              disabled={page === 1 || productosQuery.isFetching}
              className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10 disabled:opacity-50"
            >
              Página anterior
            </button>
            <p className="text-sm text-slate-300">
              Página {page}{productosQuery.isFetching ? " · actualizando..." : ""}
            </p>
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

      <ProductoModal
        open={open}
        initialData={selected}
        categorias={categoriasQuery.data ?? []}
        ingredientes={ingredientesQuery.data ?? []}
        unidadesMedida={unidadesQuery.data ?? []}
        saving={isSaving}
        error={formError}
        onClose={handleClose}
        onSubmit={handleSubmit}
      />
    </PageContainer>
  );
}
