import { useEffect, useMemo, useState } from "react";

import Modal from "../common/Modal";
import FormError from "../common/FormError";
import type { Categoria } from "../../types/categoria";
import type { Ingrediente } from "../../types/ingrediente";
import type {
  Producto,
  ProductoIngredientePayload,
  ProductoPayload,
} from "../../types/producto";
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
type ProductoIngredienteFormConfig = Omit<
  ProductoIngredientePayload,
  "cantidad"
> & { cantidad: string };

function decimalToInput(value: unknown, fallback = "1") {
  if (value === null || value === undefined || value === "") return fallback;
  return String(value).replace(",", ".");
}

function parseDecimalInput(value: string, fallback = 1) {
  const normalized = value.trim().replace(",", ".");
  if (!normalized) return fallback;
  const parsed = Number(normalized);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function parsePercentInput(value: string, fallback = 0) {
  const normalized = value.trim().replace(",", ".");
  if (!normalized) return fallback;
  const parsed = Number(normalized);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : fallback;
}

function formatMoney(value: number) {
  return `$${value.toFixed(2)}`;
}

function buildTree(categorias: Categoria[]): CategoriaNode[] {
  const map = new Map<number, CategoriaNode>();
  categorias.forEach((categoria) =>
    map.set(categoria.id, { ...categoria, hijos: [] }),
  );
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

function collectWithParents(
  categorias: Categoria[],
  selectedLeafIds: number[],
): number[] {
  const byId = new Map(
    categorias.map((categoria) => [categoria.id, categoria]),
  );
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

function getLeafIdsFromProducto(
  categorias: Categoria[],
  producto: Producto | null,
) {
  if (!producto) return [];
  const allIds = new Set(categorias.map((categoria) => categoria.id));
  const parentIds = new Set(
    categorias
      .map((categoria) => categoria.parent_id)
      .filter(Boolean) as number[],
  );
  return producto.categorias
    .filter(
      (categoria) => allIds.has(categoria.id) && !parentIds.has(categoria.id),
    )
    .map((categoria) => categoria.id);
}

function findConfig(
  configs: ProductoIngredienteFormConfig[],
  ingredienteId: number,
) {
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
  const [margenGanancia, setMargenGanancia] = useState("50");
  const [disponible, setDisponible] = useState(true);
  const [categoriaLeafIds, setCategoriaLeafIds] = useState<number[]>([]);
  const [ingredientesConfig, setIngredientesConfig] = useState<
    ProductoIngredienteFormConfig[]
  >([]);
  const [imagenesUrl, setImagenesUrl] = useState<string[]>([]);
  const [archivosImagen, setArchivosImagen] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const categoriaTree = useMemo(() => buildTree(categorias), [categorias]);
  const categoriaIdsFinales = useMemo(
    () => collectWithParents(categorias, categoriaLeafIds),
    [categorias, categoriaLeafIds],
  );
  const resumenPrecio = useMemo(() => {
    const costo = ingredientesConfig.reduce((total, config) => {
      const ingrediente = ingredientes.find((item) => item.id === config.ingrediente_id);
      const precioPorUnidad = Number(ingrediente?.precio_por_unidad ?? 0);
      const cantidad = parseDecimalInput(config.cantidad, 0);
      return total + precioPorUnidad * cantidad;
    }, 0);
    const margen = parsePercentInput(margenGanancia, 0);
    const sugerido = costo * (1 + margen / 100);
    return { costo, margen, sugerido };
  }, [ingredientesConfig, ingredientes, margenGanancia]);

  useEffect(() => {
    setNombre(initialData?.nombre ?? "");
    setDescripcion(initialData?.descripcion ?? "");
    setPrecioBase(initialData ? String(initialData.precio_base) : "0");
    setMargenGanancia(initialData ? String(initialData.margen_ganancia_porcentaje ?? 50) : "50");
    setDisponible(initialData?.disponible ?? true);
    setCategoriaLeafIds(getLeafIdsFromProducto(categorias, initialData));
    setIngredientesConfig(
      initialData?.ingredientes_configurados?.length
        ? initialData.ingredientes_configurados.map((config) => ({
            ingrediente_id: config.ingrediente_id,
            cantidad: decimalToInput(config.cantidad),
            unidad_medida_id:
              config.unidad_medida_id ??
              config.ingrediente?.unidad_medida_id ??
              null,
            es_removible: false,
          }))
        : (initialData?.ingredientes.map((ingrediente) => ({
            ingrediente_id: ingrediente.id,
            cantidad: "1",
            unidad_medida_id: ingrediente.unidad_medida_id ?? null,
            es_removible: false,
          })) ?? []),
    );
    setImagenesUrl(initialData?.imagenes_url ?? []);
    setArchivosImagen([]);
    setUploadError(null);
  }, [initialData, open, categorias]);

  function toggleCategoriaLeaf(id: number) {
    setCategoriaLeafIds((current) =>
      current.includes(id)
        ? current.filter((item) => item !== id)
        : [...current, id],
    );
  }

  function toggleIngrediente(ingrediente: Ingrediente) {
    setIngredientesConfig((current) => {
      const existing = findConfig(current, ingrediente.id);
      if (existing)
        return current.filter(
          (config) => config.ingrediente_id !== ingrediente.id,
        );
      return [
        ...current,
        {
          ingrediente_id: ingrediente.id,
          cantidad: "1",
          unidad_medida_id: ingrediente.unidad_medida_id ?? null,
          es_removible: false,
        },
      ];
    });
  }

  function updateIngredienteConfig(
    ingredienteId: number,
    changes: Partial<ProductoIngredienteFormConfig>,
  ) {
    setIngredientesConfig((current) =>
      current.map((config) =>
        config.ingrediente_id === ingredienteId
          ? { ...config, ...changes }
          : config,
      ),
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
        setUploadError(
          err instanceof Error
            ? err.message
            : "No se pudieron subir las imágenes.",
        );
        return;
      } finally {
        setUploading(false);
      }
    }

    await onSubmit({
      nombre,
      descripcion: descripcion || null,
      precio_base: Number(precioBase),
      margen_ganancia_porcentaje: parsePercentInput(margenGanancia),
      unidad_venta_id: null,
      imagenes_url: urlsFinales,
      stock_cantidad: 0,
      disponible,
      categoria_ids: categoriaLeafIds,
      ingredientes_configurados: ingredientesConfig.map((config) => {
        const ingrediente = ingredientes.find(
          (item) => item.id === config.ingrediente_id,
        );

        return {
          ...config,
          cantidad: parseDecimalInput(config.cantidad),
          unidad_medida_id:
            ingrediente?.unidad_medida_id ?? config.unidad_medida_id ?? null,
          es_removible: false,
        };
      }),
    });
  }

  function renderCategoriaNode(node: CategoriaNode, depth = 0) {
    const isLeaf = node.hijos.length === 0;
    const checked = isLeaf
      ? categoriaLeafIds.includes(node.id)
      : categoriaIdsFinales.includes(node.id);

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
          {!isLeaf ? (
            <span className="ml-auto rounded-full bg-white/10 px-2 py-0.5 text-[10px] uppercase tracking-wide">
              rama
            </span>
          ) : null}
        </label>
        {node.hijos.map((child) => renderCategoriaNode(child, depth + 1))}
      </div>
    );
  }

  return (
    <Modal
      open={open}
      title={initialData ? "Editar producto" : "Nuevo producto"}
      onClose={onClose}
    >
      <form className="space-y-5" onSubmit={handleSubmit}>
        <FormError message={error || uploadError} />

        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2 md:col-span-2">
            <label className="text-sm font-semibold text-slate-200">
              Nombre
            </label>
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
            <label className="text-sm font-semibold text-slate-200">
              Precio base/manual
            </label>
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
            <label className="text-sm font-semibold text-slate-200">
              Margen de ganancia (%)
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={margenGanancia}
              onChange={(event) => setMargenGanancia(event.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500"
              required
            />
          </div>

          <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 p-4 md:col-span-2">
            <p className="text-xs uppercase tracking-[0.25em] text-emerald-200">Precio sugerido</p>
            <div className="mt-2 grid gap-2 text-sm text-slate-200 md:grid-cols-3">
              <span>Costo ingredientes: <b>{formatMoney(resumenPrecio.costo)}</b></span>
              <span>Margen: <b>{resumenPrecio.margen.toFixed(2)}%</b></span>
              <span>Sugerido: <b className="text-emerald-100">{formatMoney(resumenPrecio.sugerido)}</b></span>
            </div>
            <button
              type="button"
              onClick={() => setPrecioBase(resumenPrecio.sugerido.toFixed(2))}
              className="mt-3 rounded-xl bg-emerald-500 px-3 py-2 text-sm font-semibold text-white hover:bg-emerald-400"
            >
              Usar precio sugerido
            </button>
          </div>

          <label className="flex items-center gap-3 rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm font-semibold text-slate-200 md:col-span-2">
            <input
              type="checkbox"
              checked={disponible}
              onChange={(event) => setDisponible(event.target.checked)}
            />
            Producto disponible para la tienda
          </label>

          <div className="space-y-2 md:col-span-2">
            <label className="text-sm font-semibold text-slate-200">
              Imágenes del producto
            </label>
            <input
              type="file"
              accept="image/png,image/jpeg,image/webp,image/gif"
              multiple
              onChange={handleFilesChange}
              className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-slate-200 file:mr-4 file:rounded-xl file:border-0 file:bg-blue-500 file:px-3 file:py-2 file:font-semibold file:text-white"
            />
            <p className="text-xs text-slate-500">
              Se suben a Cloudinary al guardar. Podés cargar varias imágenes.
            </p>
            {imagenesUrl.length ? (
              <div className="grid gap-3 sm:grid-cols-3">
                {imagenesUrl.map((url) => (
                  <div
                    key={url}
                    className="relative overflow-hidden rounded-2xl border border-white/10 bg-slate-950"
                  >
                    <img
                      src={url}
                      alt="Producto"
                      className="h-28 w-full object-cover"
                    />
                    <button
                      type="button"
                      onClick={() =>
                        setImagenesUrl((actuales) =>
                          actuales.filter((item) => item !== url),
                        )
                      }
                      className="absolute right-2 top-2 rounded-full bg-slate-950/80 px-2 py-1 text-xs font-semibold text-white hover:bg-rose-500"
                    >
                      Quitar
                    </button>
                  </div>
                ))}
              </div>
            ) : null}
          </div>

          <div className="space-y-2 md:col-span-2">
            <label className="text-sm font-semibold text-slate-200">
              Descripción
            </label>
            <textarea
              value={descripcion}
              onChange={(event) => setDescripcion(event.target.value)}
              className="min-h-28 w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500"
              placeholder="Descripción opcional"
              maxLength={255}
            />
          </div>

          <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 md:col-span-2">
            <h4 className="mb-2 text-sm font-semibold text-white">
              Categorías en árbol
            </h4>
            <p className="mb-3 text-xs text-slate-500">
              Solo se seleccionan categorías finales. Las categorías padre se
              agregan automáticamente.
            </p>
            <div className="max-h-80 space-y-2 overflow-y-auto pr-1">
              {categoriaTree.map((categoria) => renderCategoriaNode(categoria))}
              {!categorias.length ? (
                <p className="text-sm text-slate-400">
                  No hay categorías disponibles.
                </p>
              ) : null}
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 md:col-span-2">
            <h4 className="mb-2 text-sm font-semibold text-white">
              Receta / consumo de ingredientes
            </h4>
            <p className="mb-3 text-xs text-slate-500">
              El stock del producto se calcula con estos consumos. Al confirmar
              un pedido, se descuenta de cada ingrediente usando la unidad
              definida al crear el ingrediente.
            </p>
            <div className="max-h-80 space-y-3 overflow-y-auto pr-1">
              {ingredientes.map((ingrediente) => {
                const config = findConfig(ingredientesConfig, ingrediente.id);
                const checked = Boolean(config);
                return (
                  <div
                    key={ingrediente.id}
                    className="rounded-xl border border-white/5 p-3 text-sm text-slate-200"
                  >
                    <label className="flex items-center gap-3 font-semibold">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => toggleIngrediente(ingrediente)}
                      />
                      {ingrediente.nombre}
                      <span className="ml-auto text-xs text-slate-500">
                        Stock: {ingrediente.stock_cantidad}
                        {ingrediente.unidad_medida
                          ? ` ${ingrediente.unidad_medida.simbolo}`
                          : ""} · {formatMoney(Number(ingrediente.precio_por_unidad ?? 0))}/{ingrediente.unidad_medida?.simbolo ?? "u"}
                      </span>
                    </label>

                    {config ? (
                      <div className="mt-3 grid gap-2 md:grid-cols-[minmax(0,1fr)_auto] md:items-center">
                        <input
                          type="text"
                          inputMode="decimal"
                          value={config.cantidad}
                          onChange={(event) =>
                            updateIngredienteConfig(ingrediente.id, {
                              cantidad: event.target.value,
                              unidad_medida_id:
                                ingrediente.unidad_medida_id ?? null,
                            })
                          }
                          className="rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-white outline-none"
                          placeholder="Cantidad. Ej: 1,5"
                        />
                        <span className="rounded-xl border border-emerald-400/20 bg-emerald-400/10 px-3 py-2 text-xs font-semibold text-emerald-200">
                          Unidad: {ingrediente.unidad_medida?.simbolo ?? "sin unidad"}
                        </span>
                        <span className="rounded-xl border border-sky-400/20 bg-sky-400/10 px-3 py-2 text-xs font-semibold text-sky-200 md:col-span-2">
                          Costo en receta: {formatMoney(Number(ingrediente.precio_por_unidad ?? 0) * parseDecimalInput(config.cantidad, 0))}
                        </span>
                      </div>
                    ) : null}
                  </div>
                );
              })}
              {!ingredientes.length ? (
                <p className="text-sm text-slate-400">
                  No hay ingredientes disponibles.
                </p>
              ) : null}
            </div>
          </div>
        </div>

        <div className="sticky bottom-0 z-10 -mx-6 mt-5 flex justify-end gap-3 border-t border-white/10 bg-slate-900/95 px-6 py-4 backdrop-blur">
          <button
            type="button"
            onClick={onClose}
            className="rounded-2xl border border-white/10 px-4 py-3 text-slate-200 hover:bg-white/5"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={saving || uploading}
            className="rounded-2xl bg-blue-500 px-4 py-3 font-semibold text-white hover:bg-blue-400 disabled:opacity-60"
          >
            {saving || uploading ? "Guardando..." : "Guardar"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
