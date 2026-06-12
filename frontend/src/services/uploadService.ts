import { api } from "./api";
import type { UploadImagen } from "../types/upload";

export async function uploadImagenes(files: File[], folder = "general") {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  const response = await api.post<UploadImagen[]>(`/uploads/imagenes?folder=${encodeURIComponent(folder)}`, formData);

  return response.data;
}

export async function deleteImagenCloudinary(publicId: string) {
  await api.delete("/uploads/imagenes", {
    data: { public_id: publicId },
  });
}
