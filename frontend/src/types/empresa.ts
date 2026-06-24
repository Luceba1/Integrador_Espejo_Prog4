export interface ConfiguracionEmpresa {
  id: number;
  nombre_empresa: string;
  domicilio_retiro?: string | null;
  banco?: string | null;
  titular?: string | null;
  cuit?: string | null;
  cbu?: string | null;
  alias?: string | null;
  instrucciones_transferencia?: string | null;
  updated_at: string;
}

export interface ConfiguracionEmpresaPayload {
  nombre_empresa: string;
  domicilio_retiro?: string | null;
  banco?: string | null;
  titular?: string | null;
  cuit?: string | null;
  cbu?: string | null;
  alias?: string | null;
  instrucciones_transferencia?: string | null;
}
