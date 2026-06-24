export interface DetallePedido {
  pedido_id: number;
  producto_id: number;
  cantidad: number;
  nombre_producto_snap: string;
  precio_unitario_snap: number;
  subtotal_snap: number;
  personalizacion?: Record<string, unknown> | null;
  created_at: string;
}

export interface HistorialEstadoPedido {
  id: number;
  pedido_id: number;
  estado_desde?: string | null;
  estado_hacia: string;
  usuario_id?: number | null;
  motivo?: string | null;
  created_at: string;
}

export interface Pedido {
  id: number;
  usuario_id: number;
  direccion_id?: number | null;
  estado_codigo: string;
  forma_pago_codigo: string;
  tipo_entrega: "RETIRO" | "ENVIO" | string;
  domicilio_retiro_snap?: string | null;
  datos_transferencia_snap?: string | null;
  subtotal: number;
  descuento: number;
  costo_envio: number;
  total: number;
  notas?: string | null;
  activo: boolean;
  created_at: string;
  updated_at: string;
  deleted_at?: string | null;
  detalles: DetallePedido[];
  historial_estados: HistorialEstadoPedido[];
}

export interface PedidoEstadoUpdatePayload {
  estado_codigo: string;
  motivo?: string | null;
  recuperar_stock?: boolean;
}

export interface EstadoPedido {
  id: number;
  codigo: string;
  nombre: string;
  orden: number;
  permite_cancelacion_cliente: boolean;
  es_final: boolean;
  activo: boolean;
}

export interface FormaPago {
  id: number;
  codigo: string;
  nombre: string;
  descripcion?: string | null;
  activo: boolean;
}

export interface PedidoItemCreate {
  producto_id: number;
  cantidad: number;
  personalizacion?: Record<string, unknown> | null;
}

export interface PedidoCreatePayload {
  direccion_id?: number | null;
  tipo_entrega?: "RETIRO" | "ENVIO" | string;
  forma_pago_codigo: string;
  notas?: string | null;
  descuento: number;
  costo_envio: number;
  items: PedidoItemCreate[];
}
