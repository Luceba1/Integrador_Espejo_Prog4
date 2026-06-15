import { Link } from "react-router-dom";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import PageContainer from "../components/layout/PageContainer";
import { useAuth } from "../hooks/useAuth";
import { useDashboardMetricas } from "../hooks/useAdminUsuarios";
import type {
  DashboardEstadoPedido,
  DashboardIngredienteStockBajo,
  DashboardSerieDiaria,
  DashboardTopProducto,
  DashboardVentaFormaPago,
} from "../types/admin";

const cards = [
  {
    title: "Store público",
    description: "Catálogo, carrito Zustand + localStorage y creación de pedidos como cliente.",
    to: "/store",
  },
  {
    title: "Catálogo",
    description: "Categorías, ingredientes y productos con server state y CRUD protegido.",
    to: "/admin/productos",
  },
  {
    title: "Unidades de medida",
    description: "Catálogo v7 para vender productos por unidad, kilo, litro u otra medida.",
    to: "/admin/unidades-medida",
  },
  {
    title: "Usuarios",
    description: "Panel ADMIN para listar, editar, eliminar y asignar roles.",
    to: "/admin/usuarios",
  },
  {
    title: "Cajero / Pedidos",
    description: "Gestión de estados de pedidos para ADMIN y PEDIDOS.",
    to: "/admin/pedidos",
  },
];

const moneyFormatter = new Intl.NumberFormat("es-AR", {
  style: "currency",
  currency: "ARS",
  maximumFractionDigits: 0,
});

const numberFormatter = new Intl.NumberFormat("es-AR");

const chartPalette = ["#38bdf8", "#a78bfa", "#34d399", "#f59e0b", "#fb7185", "#22d3ee", "#c084fc"];

function asNumber(value: string | number | null | undefined) {
  const parsed = Number(value ?? 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

function formatMoney(value: string | number | null | undefined) {
  return moneyFormatter.format(asNumber(value));
}

function metricVariation(value: number, singular: string, plural: string) {
  return `${numberFormatter.format(value)} ${value === 1 ? singular : plural}`;
}

function DashboardSkeleton() {
  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="h-32 animate-pulse rounded-3xl border border-white/10 bg-white/5" />
        ))}
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="h-80 animate-pulse rounded-3xl border border-white/10 bg-white/5" />
        <div className="h-80 animate-pulse rounded-3xl border border-white/10 bg-white/5" />
      </div>
    </div>
  );
}

function MetricCard({
  title,
  value,
  helper,
  badge,
}: {
  title: string;
  value: string | number;
  helper: string;
  badge?: string;
}) {
  return (
    <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-5 shadow-lg shadow-slate-950/20">
      <div className="flex items-start justify-between gap-4">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-400">{title}</p>
        {badge ? (
          <span className="rounded-full bg-sky-500/15 px-2.5 py-1 text-[0.65rem] font-bold uppercase tracking-wide text-sky-200">
            {badge}
          </span>
        ) : null}
      </div>
      <strong className="mt-4 block text-3xl text-white">{value}</strong>
      <p className="mt-2 text-sm text-slate-400">{helper}</p>
    </div>
  );
}

function SectionHeader({ title, subtitle, tag }: { title: string; subtitle: string; tag?: string }) {
  return (
    <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
      <div>
        <h3 className="text-xl font-bold text-white">{title}</h3>
        <p className="mt-1 text-sm text-slate-400">{subtitle}</p>
      </div>
      {tag ? (
        <span className="w-fit rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-semibold text-emerald-200">
          {tag}
        </span>
      ) : null}
    </div>
  );
}

function ChartTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ name?: string; value?: number }>; label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/95 p-3 text-sm shadow-xl">
      <p className="mb-2 font-semibold text-white">{label}</p>
      {payload.map((entry) => (
        <p key={`${entry.name}-${entry.value}`} className="text-slate-300">
          {entry.name}: <span className="font-semibold text-sky-200">{numberFormatter.format(asNumber(entry.value))}</span>
        </p>
      ))}
    </div>
  );
}

function MoneyTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ name?: string; value?: number }>; label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/95 p-3 text-sm shadow-xl">
      <p className="mb-2 font-semibold text-white">{label}</p>
      {payload.map((entry) => (
        <p key={`${entry.name}-${entry.value}`} className="text-slate-300">
          {entry.name}: <span className="font-semibold text-sky-200">{formatMoney(entry.value)}</span>
        </p>
      ))}
    </div>
  );
}

function EstadoPedidosChart({ data }: { data: DashboardEstadoPedido[] }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-6 shadow-lg shadow-slate-950/20">
      <SectionHeader
        title="Pedidos por estado"
        subtitle="Distribución de la máquina de estados del pedido. Permite detectar cuellos de botella del flujo operativo."
        tag="FSM + WebSocket"
      />

      {data.length === 0 ? (
        <p className="rounded-2xl bg-white/5 p-4 text-sm text-slate-400">Todavía no hay pedidos registrados.</p>
      ) : (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ left: 0, right: 16, top: 8, bottom: 8 }}>
              <CartesianGrid stroke="#334155" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="estado_codigo" stroke="#94a3b8" tick={{ fontSize: 12 }} />
              <YAxis stroke="#94a3b8" allowDecimals={false} tick={{ fontSize: 12 }} />
              <Tooltip content={<ChartTooltip />} />
              <Bar dataKey="total" name="Pedidos" radius={[10, 10, 0, 0]} fill="#38bdf8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

function WeeklyTrendChart({ data }: { data: DashboardSerieDiaria[] }) {
  const chartData = data.map((dia) => ({
    ...dia,
    ventas_numero: asNumber(dia.ventas),
  }));

  return (
    <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-6 shadow-lg shadow-slate-950/20">
      <SectionHeader
        title="Actividad de los últimos 7 días"
        subtitle="Tendencia de ventas confirmadas. Muestra evolución diaria y no solamente totales acumulados."
        tag="Tendencia"
      />

      {chartData.length === 0 ? (
        <p className="rounded-2xl bg-white/5 p-4 text-sm text-slate-400">Todavía no hay ventas confirmadas.</p>
      ) : (
        <>
          <div className="h-72 rounded-2xl bg-slate-950/50 p-3">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ left: 0, right: 16, top: 8, bottom: 8 }}>
                <defs>
                  <linearGradient id="ventasFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.5} />
                    <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#334155" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="label" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <YAxis stroke="#94a3b8" tickFormatter={(value) => `$${numberFormatter.format(Number(value))}`} tick={{ fontSize: 12 }} />
                <Tooltip content={<MoneyTooltip />} />
                <Area
                  type="monotone"
                  dataKey="ventas_numero"
                  name="Ventas"
                  stroke="#38bdf8"
                  strokeWidth={3}
                  fill="url(#ventasFill)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl bg-white/5 p-3">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Ventas en 7 días</p>
              <strong className="mt-1 block text-lg text-white">
                {formatMoney(chartData.reduce((total, dia) => total + dia.ventas_numero, 0))}
              </strong>
            </div>
            <div className="rounded-2xl bg-white/5 p-3">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Pedidos en 7 días</p>
              <strong className="mt-1 block text-lg text-white">
                {numberFormatter.format(chartData.reduce((total, dia) => total + dia.pedidos, 0))}
              </strong>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function FormaPagoChart({ data }: { data: DashboardVentaFormaPago[] }) {
  const chartData = data.map((forma) => ({
    ...forma,
    total_ventas_numero: asNumber(forma.total_ventas),
  }));

  return (
    <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-6 shadow-lg shadow-slate-950/20">
      <SectionHeader
        title="Ventas por forma de pago"
        subtitle="Comparación entre efectivo, transferencia y MercadoPago sobre pedidos confirmados."
        tag="Pagos"
      />

      {chartData.length === 0 ? (
        <p className="rounded-2xl bg-white/5 p-4 text-sm text-slate-400">Todavía no hay ventas confirmadas.</p>
      ) : (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                dataKey="total_ventas_numero"
                nameKey="forma_pago_codigo"
                innerRadius={52}
                outerRadius={92}
                paddingAngle={3}
              >
                {chartData.map((_, index) => (
                  <Cell key={index} fill={chartPalette[index % chartPalette.length]} />
                ))}
              </Pie>
              <Tooltip content={<MoneyTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

function TopProductsChart({ data }: { data: DashboardTopProducto[] }) {
  const chartData = data.map((producto) => ({
    ...producto,
    total_vendido_numero: asNumber(producto.total_vendido),
  }));

  return (
    <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-6 shadow-lg shadow-slate-950/20">
      <SectionHeader
        title="Top productos vendidos"
        subtitle="Ranking de productos con mayor cantidad vendida, calculado desde DetallePedido."
        tag="Catálogo"
      />

      {chartData.length === 0 ? (
        <p className="rounded-2xl bg-white/5 p-4 text-sm text-slate-400">Todavía no hay productos vendidos.</p>
      ) : (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical" margin={{ left: 16, right: 16, top: 8, bottom: 8 }}>
              <CartesianGrid stroke="#334155" strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" stroke="#94a3b8" allowDecimals={false} tick={{ fontSize: 12 }} />
              <YAxis type="category" dataKey="nombre" stroke="#94a3b8" width={110} tick={{ fontSize: 12 }} />
              <Tooltip content={<ChartTooltip />} />
              <Bar dataKey="unidades_vendidas" name="Unidades" radius={[0, 10, 10, 0]} fill="#f59e0b" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

function StockBajoPanel({ data }: { data: DashboardIngredienteStockBajo[] }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-6 shadow-lg shadow-slate-950/20">
      <SectionHeader
        title="Alertas de stock bajo"
        subtitle="Ingredientes con stock menor o igual a 5 unidades base. Apoya al rol STOCK del TPI."
        tag="Stock"
      />

      {data.length === 0 ? (
        <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-100">
          No hay ingredientes en nivel crítico.
        </div>
      ) : (
        <div className="overflow-hidden rounded-2xl border border-white/10">
          <table className="min-w-full divide-y divide-white/10 text-left text-sm">
            <thead className="bg-white/5 text-xs uppercase tracking-[0.18em] text-slate-400">
              <tr>
                <th className="px-4 py-3">Ingrediente</th>
                <th className="px-4 py-3 text-right">Stock</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {data.map((ingrediente) => (
                <tr key={ingrediente.ingrediente_id} className="bg-slate-950/30">
                  <td className="px-4 py-3 font-medium text-slate-100">{ingrediente.nombre}</td>
                  <td className="px-4 py-3 text-right text-amber-200">
                    {numberFormatter.format(asNumber(ingrediente.stock_cantidad))} {ingrediente.unidad_simbolo ?? ""}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default function AdminHomePage() {
  const { usuario, roles } = useAuth();
  const { data: metricas, isLoading } = useDashboardMetricas();

  return (
    <PageContainer
      title="Panel de administración"
      subtitle="Dashboard avanzado con métricas comerciales, stock, pagos y operación en tiempo real."
    >
      <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-slate-900 via-slate-900 to-sky-950/60 p-6 shadow-lg shadow-slate-950/30">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm text-slate-300">Sesión iniciada como</p>
            <h3 className="mt-1 text-2xl font-bold text-white">
              {usuario?.nombre} {usuario?.apellido ?? ""}
            </h3>
            <p className="mt-2 text-sm text-slate-400">{usuario?.email}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {roles.map((rol) => (
              <span key={rol} className="rounded-full bg-sky-500/15 px-3 py-1 text-xs font-semibold text-sky-200">
                {rol}
              </span>
            ))}
          </div>
        </div>
      </div>

      {isLoading ? (
        <DashboardSkeleton />
      ) : metricas ? (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <MetricCard
              title="Ventas confirmadas"
              value={formatMoney(metricas.ventas_confirmadas)}
              helper={`Ticket promedio: ${formatMoney(metricas.ticket_promedio)}`}
              badge="Ingresos"
            />
            <MetricCard
              title="Ventas de hoy"
              value={formatMoney(metricas.ventas_hoy)}
              helper={metricVariation(metricas.pedidos_hoy, "pedido creado hoy", "pedidos creados hoy")}
              badge="Hoy"
            />
            <MetricCard
              title="Pedidos activos"
              value={numberFormatter.format(metricas.pedidos_activos)}
              helper={`${metricas.pagos_aprobados} pagos aprobados · ${metricas.pagos_rechazados} rechazados`}
              badge="Operación"
            />
            <MetricCard
              title="Stock crítico"
              value={numberFormatter.format(metricas.stock_critico)}
              helper={`${metricas.ingredientes_activos} ingredientes activos · ${metricas.productos_activos} productos`}
              badge="Stock"
            />
          </div>

          <div className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
            <WeeklyTrendChart data={metricas.pedidos_ultimos_7_dias} />
            <EstadoPedidosChart data={metricas.pedidos_por_estado} />
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <FormaPagoChart data={metricas.ventas_por_forma_pago} />
            <TopProductsChart data={metricas.top_productos} />
          </div>

          <div className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
            <StockBajoPanel data={metricas.ingredientes_stock_bajo} />
            <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-6 shadow-lg shadow-slate-950/20">
              <SectionHeader
                title="Indicadores de catálogo y usuarios"
                subtitle="Resumen de entidades principales que alimentan el panel administrativo."
                tag="Administración"
              />
              <div className="grid gap-3 sm:grid-cols-3">
                <div className="rounded-2xl bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Productos</p>
                  <strong className="mt-2 block text-2xl text-white">{metricas.productos_activos}</strong>
                  <p className="mt-1 text-xs text-slate-400">activos</p>
                </div>
                <div className="rounded-2xl bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Ingredientes</p>
                  <strong className="mt-2 block text-2xl text-white">{metricas.ingredientes_activos}</strong>
                  <p className="mt-1 text-xs text-slate-400">con control de stock</p>
                </div>
                <div className="rounded-2xl bg-white/5 p-4">
                  <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Usuarios</p>
                  <strong className="mt-2 block text-2xl text-white">{metricas.usuarios_activos}</strong>
                  <p className="mt-1 text-xs text-slate-400">activos por RBAC</p>
                </div>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="rounded-3xl border border-amber-500/30 bg-amber-500/10 p-5 text-amber-100">
          No se pudieron cargar las métricas del dashboard.
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        {cards.map((card) => (
          <Link
            key={card.to}
            to={card.to}
            className="rounded-3xl border border-white/10 bg-slate-900/70 p-6 transition hover:-translate-y-1 hover:bg-slate-900"
          >
            <h3 className="text-xl font-bold text-white">{card.title}</h3>
            <p className="mt-3 text-sm text-slate-300">{card.description}</p>
          </Link>
        ))}
      </div>
    </PageContainer>
  );
}
