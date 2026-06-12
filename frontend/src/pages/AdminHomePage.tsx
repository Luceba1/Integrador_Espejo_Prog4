import { Link } from "react-router-dom";

import PageContainer from "../components/layout/PageContainer";
import { useAuth } from "../hooks/useAuth";

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

export default function AdminHomePage() {
  const { usuario, roles } = useAuth();

  return (
    <PageContainer
      title="Panel de administración"
      subtitle="Módulo protegido por autenticación. Las acciones se habilitan según los roles del usuario."
    >
      <div className="rounded-3xl border border-white/10 bg-white/5 p-6">
        <p className="text-sm text-slate-300">Sesión iniciada como</p>
        <h3 className="mt-1 text-2xl font-bold text-white">
          {usuario?.nombre} {usuario?.apellido ?? ""}
        </h3>
        <p className="mt-2 text-sm text-slate-400">{usuario?.email}</p>
        <div className="mt-4 flex flex-wrap gap-2">
          {roles.map((rol) => (
            <span key={rol} className="rounded-full bg-sky-500/15 px-3 py-1 text-xs font-semibold text-sky-200">
              {rol}
            </span>
          ))}
        </div>
      </div>

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
