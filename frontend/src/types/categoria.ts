export interface Categoria {
  id: number;
  parent_id?: number | null;
  nombre: string;
  descripcion?: string | null;
  imagen_url?: string | null;
  activo?: boolean;
  deleted_at?: string | null;
}

export interface CategoriaPayload {
  parent_id?: number | null;
  nombre: string;
  descripcion?: string | null;
  imagen_url?: string | null;
}
