import { useEffect, useState } from "react";

import Modal from "../common/Modal";
import FormError from "../common/FormError";
import type { Ingrediente, IngredientePayload } from "../../types/ingrediente";
import type { UnidadMedida } from "../../types/unidadMedida";

function parseDecimalInput(value: string, fallback = 0) {
  const normalized = value.trim().replace(",", ".");
  if (!normalized) return fallback;
  const parsed = Number(normalized);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : fallback;
}

export interface IngredienteModalProps {
  open: boolean;
  initialData: Ingrediente | null;
  unidadesMedida: UnidadMedida[];
  saving: boolean;
  error?: string | null;
  onClose: () => void;
  onSubmit: (payload: IngredientePayload) => Promise<void>;
}

export default function IngredienteModal({
  open,
  initialData,
  unidadesMedida,
  saving,
  error,
  onClose,
  onSubmit,
}: IngredienteModalProps) {
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [esAlergeno, setEsAlergeno] = useState(false);
  const [stockCantidad, setStockCantidad] = useState("0");
  const [precioCostoTotal, setPrecioCostoTotal] = useState("0");
  const [unidadMedidaId, setUnidadMedidaId] = useState("");

  useEffect(() => {
    setNombre(initialData?.nombre ?? "");
    setDescripcion(initialData?.descripcion ?? "");
    setEsAlergeno(initialData?.es_alergeno ?? false);
    setStockCantidad(
      initialData ? String(initialData.stock_cantidad ?? 0) : "0",
    );
    setPrecioCostoTotal(initialData ? String(initialData.precio_costo_total ?? 0) : "0");
    setUnidadMedidaId(
      initialData?.unidad_medida_id ? String(initialData.unidad_medida_id) : "",
    );
  }, [initialData, open]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit({
      nombre,
      descripcion: descripcion || null,
      es_alergeno: esAlergeno,
      stock_cantidad: parseDecimalInput(stockCantidad),
      precio_costo_total: parseDecimalInput(precioCostoTotal),
      unidad_medida_id: unidadMedidaId ? Number(unidadMedidaId) : null,
    });
  }

  return (
    <Modal
      open={open}
      title={initialData ? "Editar ingrediente" : "Nuevo ingrediente"}
      onClose={onClose}
    >
      <form className="space-y-4" onSubmit={handleSubmit}>
        <FormError message={error} />

        <div className="space-y-2">
          <label className="text-sm font-semibold text-slate-200">Nombre</label>
          <input
            value={nombre}
            onChange={(event) => setNombre(event.target.value)}
            className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none ring-0 placeholder:text-slate-500"
            placeholder="Harina, Leche, Queso, etc."
            required
            minLength={2}
            maxLength={100}
          />
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-200">
              Stock del ingrediente
            </label>
            <input
              type="text"
              inputMode="decimal"
              value={stockCantidad}
              onChange={(event) => setStockCantidad(event.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500"
              required
              placeholder="Ej: 1,5"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-200">
              Precio total comprado
            </label>
            <input
              type="text"
              inputMode="decimal"
              value={precioCostoTotal}
              onChange={(event) => setPrecioCostoTotal(event.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500"
              required
              placeholder="Ej: 5000"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-200">
              Unidad del stock
            </label>
            <select
              value={unidadMedidaId}
              onChange={(event) => setUnidadMedidaId(event.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none"
            >
              <option value="">Sin unidad</option>
              {unidadesMedida.map((unidad) => (
                <option key={unidad.id} value={unidad.id}>
                  {unidad.nombre} ({unidad.simbolo})
                </option>
              ))}
            </select>
          </div>
        </div>

        <label className="flex items-center gap-3 rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm font-semibold text-slate-200">
          <input
            type="checkbox"
            checked={esAlergeno}
            onChange={(event) => setEsAlergeno(event.target.checked)}
          />
          Marcar como alérgeno
        </label>

        <div className="space-y-2">
          <label className="text-sm font-semibold text-slate-200">
            Descripción
          </label>
          <textarea
            value={descripcion}
            onChange={(event) => setDescripcion(event.target.value)}
            className="min-h-28 w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-white outline-none placeholder:text-slate-500"
            placeholder="Descripción opcional"
            maxLength={255}
          />
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-2xl border border-white/10 px-4 py-3 text-slate-200 hover:bg-white/5"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={saving}
            className="rounded-2xl bg-blue-500 px-4 py-3 font-semibold text-white hover:bg-blue-400 disabled:opacity-60"
          >
            {saving ? "Guardando..." : "Guardar"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
