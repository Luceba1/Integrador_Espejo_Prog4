import { useEffect, useMemo, useState } from "react";

import Modal from "../common/Modal";
import FormError from "../common/FormError";
import type { Categoria } from "../../types/categoria";
import type { Ingrediente } from "../../types/ingrediente";
import type { Producto, ProductoIngredientePayload, ProductoPayload } from "../../types/producto";
import type { UnidadMedida } from "../../types/unidadMedida";
import { uploadImagenes } from "../../services/uploadService";

export interface ProductoModalProps {
  open: boolean;
  initialData: Producto | null;
  categorias: Categoria[];
  ingredientes: Ingrediente[];
  unidadesMedida: UnidadMedida[];
  saving: boolean;
  error?: string | null;
  onClose: () => void;
  onSubmit: (payload: ProductoPayload) => Promise<void>;
}

type CategoriaNode = Categoria & { hijos: CategoriaNode[] };

function buildTree(categorias: Categoria[]): CategoriaNode[] {
  const map = new Map<number, CategoriaNode>();
  categorias.forEach((categoria) => map.set(categoria.id, { ...categoria, hijos: [] }));
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

function collectWithParents(categorias: Categoria[], selectedLeafIds: number[]): number[] {
  const byId = new Map(categorias.map((categoria) => [categoria.id, categoria]));
  const result = new Set<number>();

  selectedLeafIds.forEach((id) => {
    let current = byId.get(id);
    while (current) {
      result.add(current.id);
      current = current.parent_id ? byId.get(current.parent_id) : undefined;
    }
  });

  return Array.from(result);
}

function getLeafIdsFromProducto(categorias: Categoria[], producto: Producto | null) {
  if (!producto) return [];
  const allIds = new Set(categorias.map((categoria) => categoria.id));
  const parentIds = new Set(categorias.map((categoria) => categoria.parent_id).filter(Boolean) as number[]);
  return producto.categorias
    .filter((categoria) => allIds.has(categoria.id) && !parentIds.has(categoria.id))
    .map((categoria) => categoria.id);
}

function findConfig(configs: ProductoIngredientePayload[], ingredienteId: number) {
  return configs.find((config) => config.ingrediente_id === ingredienteId);
}

export default function ProductoModal({
  open,
  initialData,
  categorias,
  ingredientes,
  unidadesMedida,
  saving,
  error,
  onClose,
  onSubmit,
}: ProductoModalProps) {
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [precioBase, setPrecioBase] = useState("0");
  const [unidadVentaId, setUnidadVentaId] = useState("");
  const [disponible, setDisponible] = useState(true);
  const [categoriaLeafIds, setCategoriaLeafIds] = useState<number[]>([]);
  const [ingredientesConfig, setIngredientesConfig] = useState<ProductoIngredientePayload[]>([]);
  const [imagenesUrl, setImagenesUrl] = useState<string[]>([]);
  const [archivosImagen, setArchivosImagen] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const categoriaTree = useMemo(() => buildTree(categorias), [categorias]);
  const categoriaIdsFinales = useMemo(() => collectWithParents(categorias, categoriaLeafIds), [categorias, categoriaLeafIds]);

  useEffect(() => {
    setNombre(initialData?.nombre ?? "");
    setDescripcion(initialData?.descripcion ?? "");
    setPrecioBase(initialData ? String(initialData.precio_base) : "0");
    setUnidadVentaId(initialData?.unidad_venta_id ? String(initialData.unidad_venta_id) : "");
    setDisponible(initialData?.disponible ?? true);
    setCategoriaLeafIds(getLeafIdsFromProducto(categorias, initialData));
    setIngredientesConfig(
      initialData?.ingredientes_configurados?.length
        ? initialData.ingredientes_configurados.map((config) => ({
            ingrediente_id: config.ingrediente_id,
            cantidad: Number(config.cantidad),
            unidad_medida_id: config.unidad_medida_id ?? config.ingrediente?.unidad_medida_id ?? null,
            es_removible: config.es_removible,
          }))
        : initialData?.ingredientes.map((ingrediente) => ({
            ingrediente_id: ingrediente.id,
            cantidad: 1,
            unidad_medida_id: ingrediente.unidad_medida_id ?? null,
            es_removible: true,
          })) ?? []
    );
    setImagenesUrl(initialData?.imagenes_url ?? []);
    setArchivosImagen([]);
    setUploadError(null);
  }, [initialData, open, categorias]);

  function toggleCategoriaLeaf(id: number) {
    setCategoriaLeafIds((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id]);
  }

  function toggleIngrediente(ingrediente: Ingrediente) {
    setIngredientesConfig((current) => {
      const existing = findConfig(current, ingrediente.id);
      if (existing) return current.filter((config) => config.ingrediente_id !== ingrediente.id);
      return [...current, { ingrediente_id: ingrediente.id, cantidad: 1, unidad_medida_id: ingrediente.unidad_medida_id ?? null, es_removible: true }];
    });
  }

  function updateIngredienteConfig(ingredienteId: number, changes: Partial<ProductoIngredientePayload>) {
    setIngredientesConfig((current) =>
      current.map((config) => config.ingrediente_id === ingredienteId ? { ...config, ...changes } : config)
    );
  }

  function handleFilesChange(event: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    setArchivosImagen(files);
    setUploadError(null);
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    let urlsFinales = imagenesUrl;

    if (archivosImagen.length) {
      try {
        setUploading(true);
        setUploadError(null);
        const uploads = await uploadImagenes(archivosImagen, "productos");
        urlsFinales = [...imagenesUrl, ...uploads.map((imagen) => imagen.url)];
        setImagenesUrl(urlsFinales);
      } catch (err) {
        setUploadError(err instanceof Error ? err.message : "No se pudieron subir las imágenes.");
        return;
      } finally {
        setUploading(false);
      }
    }

    await onSubmit({
      nombre,
      descripcion: descripcion || null,
      precio_base: Number(precioBase),
      unidad_venta_id: unidadVentaId ? Number(unidadVentaId) : null,
      imagenes_url: urlsFinales,
      stock_cantidad: 0,
      disponible,
      categoria_ids: categoriaLeafIds,
      ingredientes_configurados: ingredientesConfig,
    });
  }

  function renderCategoriaNode(node: CategoriaNode, depth = 0) {
    const isLeaf = node.hijos.length === 0;
    const checked = isLeaf ? categoriaLeafIds.includes(node.id) : categoriaIdsFinales.includes(node.id);

    return (
      <div key={node.id} className="space-y-1">
        <label
          className={`flex items-center gap-3 rounded-xl border border-white/5 px-3 py-2 text-sm ${isLeaf ? "text-slate-100" : "text-slate-400"}`}
          style={{ marginLeft: depth * 16 }}
        >
          <input
            type="checkbox"
            checked={checked}
            disabled={!isLeaf}
            onChange={() => isLeaf && toggleCategoriaLeaf(node.id)}
          />
          <span>{node.nombre}</span>
          {!isLeaf ? <span className="ml-auto rounded-full bg-white/10 px-2 py-0.5 text-[10px] uppercase tracking-wide">rama</span> : null}
        </label>
        {node.hijos.map((child) => renderCategoriaNode(child, depth + 1))}
      </div>
    );
  }

  return (
    <Modal open={open} title={initialData ? "Editar producto" : "Nuevo producto"} onClose={onClose}>
      <form className="space-y-5" onSubmit={handleSubmit}>
        <FormError message={error || uploadError} />

        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2 md:col-span-2">
            <label className="text-sm font-semibold text-slate-200">Nombre</label>
            <input
              value={nombre}
              onChange={(event) => setNombre(event.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500"
              placeholder="Pizza muzzarella, Café latte..."
              required
              minLength={2}
              maxLength={120}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-200">Precio base</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={precioBase}
              onChange={(event) => setPrecioBase(event.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500"
              required
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-200">Unidad de venta</label>
            <select
              value={unidadVentaId}
              onChange={(event) => setUnidadVentaId(event.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
            >
              <option value="">Sin unidad</option>
              {unidadesMedida.map((unidad) => (
                <option key={unidad.id} value={unidad.id}>{unidad.nombre} ({unidad.simbolo})</option>
              ))}
            </select>
          </div>

          <label className="flex items-center gap-3 rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm font-semibold text-slate-200 md:col-span-2">
            <input type="checkbox" checked={disponible} onChange={(event) => setDisponible(event.target.checked)} />
            Producto disponible para la tienda
          </label>

          <div className="space-y-2 md:col-span-2">
            <label className="text-sm font-semibold text-slate-200">Imágenes del producto</label>
            <input
              type="file"
              accept="image/png,image/jpeg,image/webp,image/gif"
              multiple
              onChange={handleFilesChange}
              className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-slate-200 file:mr-4 file:rounded-xl file:border-0 file:bg-blue-500 file:px-3 file:py-2 file:font-semibold file:text-white"
            />
            <p className="text-xs text-slate-500">Se suben a Cloudinary al guardar. Podés cargar varias imágenes.</p>
            {imagenesUrl.length ? (
              <div className="grid gap-3 sm:grid-cols-3">
                {imagenesUrl.map((url) => (
                  <div key={url} className="relative overflow-hidden rounded-2xl border border-white/10 bg-slate-950">
                    <img src={url} alt="Producto" className="h-28 w-full object-cover" />
                    <button type="button" onClick={() => setImagenesUrl((actuales) => actuales.filter((item) => item !== url))} className="absolute right-2 top-2 rounded-full bg-slate-950/80 px-2 py-1 text-xs font-semibold text-white hover:bg-rose-500">Quitar</button>
                  </div>
                ))}
              </div>
            ) : null}
          </div>

          <div className="space-y-2 md:col-span-2">
            <label className="text-sm font-semibold text-slate-200">Descripción</label>
            <textarea
              value={descripcion}
              onChange={(event) => setDescripcion(event.target.value)}
              className="min-h-28 w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500"
              placeholder="Descripción opcional"
              maxLength={255}
            />
          </div>

          <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 md:col-span-2">
            <h4 className="mb-2 text-sm font-semibold text-white">Categorías en árbol</h4>
            <p className="mb-3 text-xs text-slate-500">Solo se seleccionan categorías finales. Las categorías padre se agregan automáticamente.</p>
            <div className="max-h-80 space-y-2 overflow-y-auto pr-1">
              {categoriaTree.map((categoria) => renderCategoriaNode(categoria))}
              {!categorias.length ? <p className="text-sm text-slate-400">No hay categorías disponibles.</p> : null}
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 md:col-span-2">
            <h4 className="mb-2 text-sm font-semibold text-white">Receta / consumo de ingredientes</h4>
            <p className="mb-3 text-xs text-slate-500">El stock del producto se calcula con estos consumos. Al confirmar un pedido, se descuenta de cada ingrediente.</p>
            <div className="max-h-80 space-y-3 overflow-y-auto pr-1">
              {ingredientes.map((ingrediente) => {
                const config = findConfig(ingredientesConfig, ingrediente.id);
                const checked = Boolean(config);
                return (
                  <div key={ingrediente.id} className="rounded-xl border border-white/5 p-3 text-sm text-slate-200">
                    <label className="flex items-center gap-3 font-semibold">
                      <input type="checkbox" checked={checked} onChange={() => toggleIngrediente(ingrediente)} />
                      {ingrediente.nombre}
                      <span className="ml-auto text-xs text-slate-500">Stock: {ingrediente.stock_cantidad}{ingrediente.unidad_medida ? ` ${ingrediente.unidad_medida.simbolo}` : ""}</span>
                    </label>

                    {config ? (
                      <div className="mt-3 grid gap-2 md:grid-cols-[1fr_1fr_auto]">
                        <input
                          type="number"
                          min="0.001"
                          step="0.001"
                          value={config.cantidad}
                          onChange={(event) => updateIngredienteConfig(ingrediente.id, { cantidad: Number(event.target.value) })}
                          className="rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-white outline-none"
                          placeholder="Cantidad"
                        />
                        <select
                          value={config.unidad_medida_id ?? ""}
                          onChange={(event) => updateIngredienteConfig(ingrediente.id, { unidad_medida_id: event.target.value ? Number(event.target.value) : null })}
                          className="rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-white outline-none"
                        >
                          <option value="">Sin unidad</option>
                          {unidadesMedida.map((unidad) => <option key={unidad.id} value={unidad.id}>{unidad.simbolo}</option>)}
                        </select>
                        <label className="flex items-center gap-2 text-xs text-slate-400">
                          <input type="checkbox" checked={config.es_removible} onChange={(event) => updateIngredienteConfig(ingrediente.id, { es_removible: event.target.checked })} />
                          Removible
                        </label>
                      </div>
                    ) : null}
                  </div>
                );
              })}
              {!ingredientes.length ? <p className="text-sm text-slate-400">No hay ingredientes disponibles.</p> : null}
            </div>
          </div>
        </div>

        <div className="sticky bottom-0 z-10 -mx-6 mt-5 flex justify-end gap-3 border-t border-white/10 bg-slate-900/95 px-6 py-4 backdrop-blur">
          <button type="button" onClick={onClose} className="rounded-2xl border border-white/10 px-4 py-3 text-slate-200 hover:bg-white/5">Cancelar</button>
          <button type="submit" disabled={saving || uploading} className="rounded-2xl bg-blue-500 px-4 py-3 font-semibold text-white hover:bg-blue-400 disabled:opacity-60">
            {saving || uploading ? "Guardando..." : "Guardar"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
