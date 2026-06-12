import type { Categoria } from "./categoria";
import type { Ingrediente } from "./ingrediente";
import type { UnidadMedida } from "./unidadMedida";

export interface ProductoIngredienteConfigurado {
  ingrediente_id: number;
  ingrediente?: Pick<Ingrediente, "id" | "nombre" | "es_alergeno" | "stock_cantidad" | "unidad_medida" | "unidad_medida_id"> | null;
  cantidad: number;
  unidad_medida_id?: number | null;
  unidad_medida?: UnidadMedida | null;
  es_removible: boolean;
}

export interface Producto {
  id: number;
  nombre: string;
  descripcion?: string | null;
  precio_base: number;
  unidad_venta_id?: number | null;
  unidad_venta?: UnidadMedida | null;
  imagenes_url: string[];
  /** Stock calculado: unidades que pueden prepararse con el stock actual de ingredientes. */
  stock_cantidad: number;
  disponible: boolean;
  activo: boolean;
  deleted_at?: string | null;
  categorias: Pick<Categoria, "id" | "nombre" | "parent_id">[];
  ingredientes: Pick<Ingrediente, "id" | "nombre" | "es_alergeno" | "stock_cantidad" | "unidad_medida" | "unidad_medida_id">[];
  ingredientes_configurados?: ProductoIngredienteConfigurado[];
}

export interface ProductoIngredientePayload {
  ingrediente_id: number;
  cantidad: number;
  unidad_medida_id?: number | null;
  es_removible: boolean;
}

export interface ProductoPayload {
  nombre: string;
  descripcion?: string | null;
  precio_base: number;
  unidad_venta_id?: number | null;
  imagenes_url?: string[];
  stock_cantidad?: number;
  disponible: boolean;
  categoria_ids: number[];
  ingrediente_ids?: number[];
  ingredientes_configurados: ProductoIngredientePayload[];
}

export interface ProductoDisponibilidadPayload {
  disponible: boolean;
}

export interface ProductoStockPayload {
  stock_cantidad: number;
}
