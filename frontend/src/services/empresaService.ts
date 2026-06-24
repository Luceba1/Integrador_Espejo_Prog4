import { api } from "./api";
import type { ConfiguracionEmpresa, ConfiguracionEmpresaPayload } from "../types/empresa";

export async function getConfiguracionEmpresa() {
  const response = await api.get<ConfiguracionEmpresa>("/empresa/configuracion");
  return response.data;
}

export async function updateConfiguracionEmpresa(payload: ConfiguracionEmpresaPayload) {
  const response = await api.put<ConfiguracionEmpresa>("/empresa/configuracion", payload);
  return response.data;
}
