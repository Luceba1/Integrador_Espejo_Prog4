import type { UnidadMedida } from "./unidadMedida";

export interface Ingrediente {
  id: number;
  nombre: string;
  descripcion?: string | null;
  es_alergeno: boolean;
  stock_cantidad: number;
  unidad_medida_id?: number | null;
  unidad_medida?: UnidadMedida | null;
  activo?: boolean;
  deleted_at?: string | null;
}

export interface IngredientePayload {
  nombre: string;
  descripcion?: string | null;
  es_alergeno?: boolean;
  stock_cantidad?: number;
  unidad_medida_id?: number | null;
}
