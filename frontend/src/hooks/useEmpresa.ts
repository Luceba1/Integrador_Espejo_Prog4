import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getConfiguracionEmpresa, updateConfiguracionEmpresa } from "../services/empresaService";
import type { ConfiguracionEmpresaPayload } from "../types/empresa";

export function useConfiguracionEmpresa() {
  return useQuery({
    queryKey: ["empresa", "configuracion"],
    queryFn: getConfiguracionEmpresa,
  });
}

export function useActualizarConfiguracionEmpresa() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ConfiguracionEmpresaPayload) => updateConfiguracionEmpresa(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["empresa", "configuracion"] });
    },
  });
}
