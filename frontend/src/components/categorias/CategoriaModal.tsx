import { useEffect, useMemo, useState } from "react";

import Modal from "../common/Modal";
import FormError from "../common/FormError";
import type { Categoria, CategoriaPayload } from "../../types/categoria";
import { uploadImagenes } from "../../services/uploadService";

export interface CategoriaModalProps {
  open: boolean;
  initialData: Categoria | null;
  categorias: Categoria[];
  defaultParentId?: number | null;
  saving: boolean;
  error?: string | null;
  onClose: () => void;
  onSubmit: (payload: CategoriaPayload) => Promise<void>;
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

function flattenTree(nodes: CategoriaNode[], depth = 0): Array<{ node: CategoriaNode; depth: number }> {
  return nodes.flatMap((node) => [{ node, depth }, ...flattenTree(node.hijos, depth + 1)]);
}

function collectDescendantIds(categorias: Categoria[], categoriaId: number | null): Set<number> {
  const result = new Set<number>();
  if (!categoriaId) return result;

  const childrenByParent = new Map<number, Categoria[]>();
  categorias.forEach((categoria) => {
    if (categoria.parent_id) {
      childrenByParent.set(categoria.parent_id, [...(childrenByParent.get(categoria.parent_id) ?? []), categoria]);
    }
  });

  const visit = (id: number) => {
    for (const child of childrenByParent.get(id) ?? []) {
      result.add(child.id);
      visit(child.id);
    }
  };

  visit(categoriaId);
  return result;
}

export default function CategoriaModal({
  open,
  initialData,
  categorias,
  defaultParentId = null,
  saving,
  error,
  onClose,
  onSubmit,
}: CategoriaModalProps) {
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [parentId, setParentId] = useState<string>("");
  const [imagenUrl, setImagenUrl] = useState<string | null>(null);
  const [archivoImagen, setArchivoImagen] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const treeOptions = useMemo(() => flattenTree(buildTree(categorias)), [categorias]);
  const blockedParentIds = useMemo(() => {
    const blocked = collectDescendantIds(categorias, initialData?.id ?? null);
    if (initialData?.id) blocked.add(initialData.id);
    return blocked;
  }, [categorias, initialData]);

  useEffect(() => {
    setNombre(initialData?.nombre ?? "");
    setDescripcion(initialData?.descripcion ?? "");
    setParentId(initialData?.parent_id ? String(initialData.parent_id) : defaultParentId ? String(defaultParentId) : "");
    setImagenUrl(initialData?.imagen_url ?? null);
    setArchivoImagen(null);
    setUploadError(null);
  }, [initialData, open, defaultParentId]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    let urlFinal = imagenUrl;

    if (archivoImagen) {
      try {
        setUploading(true);
        setUploadError(null);
        const [upload] = await uploadImagenes([archivoImagen], "categorias");
        urlFinal = upload.url;
        setImagenUrl(urlFinal);
      } catch (err) {
        setUploadError(err instanceof Error ? err.message : "No se pudo subir la imagen.");
        return;
      } finally {
        setUploading(false);
      }
    }

    await onSubmit({
      parent_id: parentId ? Number(parentId) : null,
      nombre,
      descripcion: descripcion || null,
      imagen_url: urlFinal,
    });
  }

  return (
    <Modal
      open={open}
      title={initialData ? "Editar categoría" : parentId ? "Nueva subcategoría" : "Nueva categoría"}
      onClose={onClose}
    >
      <form className="space-y-4" onSubmit={handleSubmit}>
        <FormError message={error || uploadError} />

        <div className="rounded-2xl border border-blue-500/20 bg-blue-500/10 px-4 py-3 text-sm text-blue-100">
          <p className="font-semibold">Jerarquía</p>
          <p className="mt-1 text-blue-100/80">
            Elegí una categoría padre para crear una rama hija. Si dejás “Raíz”, la categoría queda en el primer nivel.
          </p>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-semibold text-slate-200">Categoría padre</label>
          <select
            value={parentId}
            onChange={(event) => setParentId(event.target.value)}
            className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none ring-0"
          >
            <option value="">Raíz / sin padre</option>
            {treeOptions.map(({ node, depth }) => (
              <option key={node.id} value={node.id} disabled={blockedParentIds.has(node.id)}>
                {`${"— ".repeat(depth)}${node.nombre}${blockedParentIds.has(node.id) ? " (no disponible)" : ""}`}
              </option>
            ))}
          </select>
          <p className="text-xs text-slate-500">
            No se permite elegir la misma categoría ni una categoría hija como padre, para evitar ciclos.
          </p>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-semibold text-slate-200">Nombre</label>
          <input
            value={nombre}
            onChange={(event) => setNombre(event.target.value)}
            className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none ring-0 placeholder:text-slate-500"
            placeholder="Bebidas, Sin alcohol, Sin gas, etc."
            required
            minLength={2}
            maxLength={100}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-semibold text-slate-200">Imagen de categoría</label>
          <input
            type="file"
            accept="image/png,image/jpeg,image/webp,image/gif"
            onChange={(event) => setArchivoImagen(event.target.files?.[0] ?? null)}
            className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-slate-200 file:mr-4 file:rounded-xl file:border-0 file:bg-blue-500 file:px-3 file:py-2 file:font-semibold file:text-white"
          />
          <p className="text-xs text-slate-500">La imagen se sube a Cloudinary al guardar.</p>
          {imagenUrl ? (
            <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-slate-950">
              <img src={imagenUrl} alt="Categoría" className="h-36 w-full object-cover" />
              <button
                type="button"
                onClick={() => setImagenUrl(null)}
                className="absolute right-2 top-2 rounded-full bg-slate-950/80 px-2 py-1 text-xs font-semibold text-white hover:bg-rose-500"
              >
                Quitar
              </button>
            </div>
          ) : null}
        </div>

        <div className="space-y-2">
          <label className="text-sm font-semibold text-slate-200">Descripción</label>
          <textarea
            value={descripcion}
            onChange={(event) => setDescripcion(event.target.value)}
            className="min-h-28 w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500"
            placeholder="Descripción opcional"
            maxLength={255}
          />
        </div>

        <div className="flex justify-end gap-3 pt-2">
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
