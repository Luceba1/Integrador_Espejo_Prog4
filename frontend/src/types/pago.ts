export interface PagoCrearResponse {
  pago_id: number;
  preference_id: string;
  init_point?: string | null;
  sandbox_init_point?: string | null;
  public_key?: string | null;
}

export interface PagoEstadoResponse {
  estado?: string | null;
  pedido_id: number;
  pedido_estado?: string | null;
}
