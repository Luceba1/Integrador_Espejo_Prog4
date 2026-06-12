export interface UnidadMedida {
  id: number;
  nombre: string;
  simbolo: string;
  tipo: string;
  activo: boolean;
  created_at: string;
  updated_at: string;
  deleted_at?: string | null;
}

export interface UnidadMedidaPayload {
  nombre: string;
  simbolo: string;
  tipo: string;
  activo?: boolean;
}
