import type { Rol } from "./auth";

export interface UsuarioAdmin {
  id: number;
  email: string;
  nombre: string;
  apellido?: string | null;
  activo: boolean;
  roles: Rol[];
  created_at: string;
  updated_at: string;
  deleted_at?: string | null;
}

export interface UsuarioAdminUpdatePayload {
  email?: string;
  nombre?: string;
  apellido?: string | null;
  activo?: boolean;
}

export interface UsuarioRolesUpdatePayload {
  roles: string[];
}

export interface DashboardEstadoPedido {
  estado_codigo: string;
  total: number;
}

export interface DashboardVentaFormaPago {
  forma_pago_codigo: string;
  total_pedidos: number;
  total_ventas: string | number;
}

export interface DashboardSerieDiaria {
  fecha: string;
  label: string;
  pedidos: number;
  ventas: string | number;
}

export interface DashboardTopProducto {
  producto_id: number;
  nombre: string;
  unidades_vendidas: number;
  total_vendido: string | number;
}

export interface DashboardIngredienteStockBajo {
  ingrediente_id: number;
  nombre: string;
  stock_cantidad: string | number;
  unidad_simbolo?: string | null;
}

export interface DashboardMetricas {
  productos_activos: number;
  ingredientes_activos: number;
  usuarios_activos: number;
  pedidos_activos: number;
  pedidos_hoy: number;
  pagos_aprobados: number;
  pagos_rechazados: number;
  stock_critico: number;
  ventas_confirmadas: string | number;
  ventas_hoy: string | number;
  ticket_promedio: string | number;
  pedidos_por_estado: DashboardEstadoPedido[];
  ventas_por_forma_pago: DashboardVentaFormaPago[];
  pedidos_ultimos_7_dias: DashboardSerieDiaria[];
  top_productos: DashboardTopProducto[];
  ingredientes_stock_bajo: DashboardIngredienteStockBajo[];
}
