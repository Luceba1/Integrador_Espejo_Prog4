export interface CarritoItem {
  producto_id: number;
  nombre: string;
  precio_unitario: number;
  imagen_url?: string | null;
  cantidad: number;
  stock_cantidad: number;
}

export interface CarritoState {
  items: CarritoItem[];
}
