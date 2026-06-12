import { api } from "./api";

export type ExportResource = "productos" | "categorias" | "ingredientes" | "unidades-medida" | "usuarios";

const FILENAMES: Record<ExportResource, string> = {
  productos: "productos.xlsx",
  categorias: "categorias.xlsx",
  ingredientes: "ingredientes.xlsx",
  "unidades-medida": "unidades_medida.xlsx",
  usuarios: "usuarios.xlsx",
};

export async function descargarExcel(resource: ExportResource, incluirEliminados = true) {
  const response = await api.get<Blob>(`/export/${resource}.xlsx`, {
    params: resource === "categorias" || resource === "unidades-medida"
      ? { incluir_eliminadas: incluirEliminados }
      : { incluir_eliminados: incluirEliminados },
    responseType: "blob",
  });

  const url = window.URL.createObjectURL(response.data);
  const link = document.createElement("a");
  link.href = url;
  link.download = FILENAMES[resource];
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
