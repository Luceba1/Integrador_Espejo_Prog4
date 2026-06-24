import { useEffect, useState } from "react";

import PageContainer from "../components/layout/PageContainer";
import {
  useActualizarConfiguracionEmpresa,
  useConfiguracionEmpresa,
} from "../hooks/useEmpresa";
import type { ConfiguracionEmpresaPayload } from "../types/empresa";

const EMPTY_FORM: ConfiguracionEmpresaPayload = {
  nombre_empresa: "FoodStore",
  domicilio_retiro: "",
  banco: "",
  titular: "",
  cuit: "",
  cbu: "",
  alias: "",
  instrucciones_transferencia: "",
};

function normalizePayload(
  payload: ConfiguracionEmpresaPayload,
): ConfiguracionEmpresaPayload {
  return Object.fromEntries(
    Object.entries(payload).map(([key, value]) => [
      key,
      typeof value === "string" ? value.trim() || null : value,
    ]),
  ) as ConfiguracionEmpresaPayload;
}

export default function EmpresaConfigPage() {
  const configQuery = useConfiguracionEmpresa();
  const actualizarMutation = useActualizarConfiguracionEmpresa();
  const [form, setForm] = useState<ConfiguracionEmpresaPayload>(EMPTY_FORM);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!configQuery.data) return;
    setForm({
      nombre_empresa: configQuery.data.nombre_empresa ?? "FoodStore",
      domicilio_retiro: configQuery.data.domicilio_retiro ?? "",
      banco: configQuery.data.banco ?? "",
      titular: configQuery.data.titular ?? "",
      cuit: configQuery.data.cuit ?? "",
      cbu: configQuery.data.cbu ?? "",
      alias: configQuery.data.alias ?? "",
      instrucciones_transferencia:
        configQuery.data.instrucciones_transferencia ?? "",
    });
  }, [configQuery.data]);

  function updateField(
    field: keyof ConfiguracionEmpresaPayload,
    value: string,
  ) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);
    setError(null);

    if (!form.nombre_empresa.trim()) {
      setError("Completá el nombre de la empresa.");
      return;
    }

    try {
      await actualizarMutation.mutateAsync(normalizePayload(form));
      setMessage("Datos de empresa actualizados correctamente.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "No se pudo actualizar la configuración de empresa.",
      );
    }
  }

  return (
    <PageContainer
      title="Empresa"
      subtitle="Configurá los datos que ve el comprador cuando elige transferencia o retiro en el lugar."
    >
      {configQuery.isLoading ? (
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-slate-300">
          Cargando configuración...
        </div>
      ) : null}
      {configQuery.isError ? (
        <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-rose-200">
          No se pudo cargar la configuración.
        </div>
      ) : null}

      <form
        onSubmit={handleSubmit}
        className="space-y-6 rounded-3xl border border-white/10 bg-slate-900/70 p-6"
      >
        {message ? (
          <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-emerald-100">
            {message}
          </div>
        ) : null}
        {error ? (
          <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-rose-100">
            {error}
          </div>
        ) : null}

        <div className="space-y-2">
          <label className="text-sm font-semibold text-slate-200">
            Nombre de la empresa
          </label>
          <input
            value={form.nombre_empresa}
            onChange={(event) =>
              updateField("nombre_empresa", event.target.value)
            }
            className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
            placeholder="FoodStore"
          />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <section className="rounded-3xl border border-emerald-400/20 bg-emerald-500/5 p-5">
            <h3 className="text-lg font-bold text-white">Retiro en el lugar</h3>
            <p className="mt-1 text-sm text-slate-400">
              Estos datos se muestran cuando el cliente elige retirar el pedido.
            </p>
            <div className="mt-4 space-y-3">
              <textarea
                value={form.domicilio_retiro ?? ""}
                onChange={(event) =>
                  updateField("domicilio_retiro", event.target.value)
                }
                className="min-h-24 w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
                placeholder="Domicilio de retiro"
              />
            </div>
          </section>

          <section className="rounded-3xl border border-sky-400/20 bg-sky-500/5 p-5">
            <h3 className="text-lg font-bold text-white">Datos bancarios</h3>
            <p className="mt-1 text-sm text-slate-400">
              Estos datos se muestran cuando el cliente elige transferencia.
            </p>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <input
                value={form.banco ?? ""}
                onChange={(event) => updateField("banco", event.target.value)}
                className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
                placeholder="Banco"
              />
              <input
                value={form.titular ?? ""}
                onChange={(event) => updateField("titular", event.target.value)}
                className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
                placeholder="Titular"
              />
              <input
                value={form.cuit ?? ""}
                onChange={(event) => updateField("cuit", event.target.value)}
                className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
                placeholder="CUIT"
              />
              <input
                value={form.cbu ?? ""}
                onChange={(event) => updateField("cbu", event.target.value)}
                className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
                placeholder="CBU / CVU"
              />
              <input
                value={form.alias ?? ""}
                onChange={(event) => updateField("alias", event.target.value)}
                className="rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none md:col-span-2"
                placeholder="Alias"
              />
              <textarea
                value={form.instrucciones_transferencia ?? ""}
                onChange={(event) =>
                  updateField("instrucciones_transferencia", event.target.value)
                }
                className="min-h-24 rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none md:col-span-2"
                placeholder="Instrucciones para el comprador"
              />
            </div>
          </section>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={actualizarMutation.isPending}
            className="rounded-2xl bg-emerald-500 px-5 py-3 font-semibold text-white hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {actualizarMutation.isPending
              ? "Guardando..."
              : "Guardar datos de empresa"}
          </button>
        </div>
      </form>
    </PageContainer>
  );
}
