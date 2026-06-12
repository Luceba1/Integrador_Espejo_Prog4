export interface UploadImagen {
  public_id: string;
  url: string;
  formato?: string | null;
  ancho?: number | null;
  alto?: number | null;
  bytes?: number | null;
  nombre_archivo?: string | null;
}
