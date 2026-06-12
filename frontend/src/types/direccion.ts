export interface DireccionEntrega {
  id: number;
  usuario_id: number;
  etiqueta?: string | null;
  linea1: string;
  linea2?: string | null;
  ciudad: string;
  latitud?: number | null;
  longitud?: number | null;
  es_principal: boolean;
  activo: boolean;
  created_at: string;
  updated_at: string;
  deleted_at?: string | null;
}

export interface DireccionPayload {
  etiqueta?: string | null;
  linea1: string;
  linea2?: string | null;
  ciudad: string;
  latitud?: number | null;
  longitud?: number | null;
  es_principal: boolean;
}
