import { NavLink, useNavigate } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";

interface NavItem {
  to: string;
  label: string;
  roles?: string[];
}

const links: NavItem[] = [
  { to: "/admin", label: "Inicio" },
  { to: "/store", label: "Store" },
  { to: "/admin/productos", label: "Productos", roles: ["ADMIN", "STOCK"] },
  { to: "/admin/categorias", label: "Categorías", roles: ["ADMIN", "STOCK"] },
  { to: "/admin/ingredientes", label: "Ingredientes", roles: ["ADMIN", "STOCK"] },
  { to: "/admin/unidades-medida", label: "Unidades", roles: ["ADMIN", "STOCK"] },
  { to: "/admin/pedidos", label: "Pedidos", roles: ["ADMIN", "PEDIDOS"] },
  { to: "/admin/usuarios", label: "Usuarios", roles: ["ADMIN"] },
];

export default function Navbar() {
  const navigate = useNavigate();
  const { hasRole, logout, roles, usuario } = useAuth();

  async function handleLogout() {
    await logout();
    navigate("/login", { replace: true });
  }

  const visibleLinks = links.filter((link) => !link.roles || hasRole(...link.roles));

  return (
    <header className="border-b border-white/10 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.25em] text-blue-300">
              Programación IV
            </p>
            <h1 className="text-2xl font-bold text-white">Parcial 2 · Administración</h1>
            {usuario ? (
              <p className="mt-1 text-sm text-slate-400">
                {usuario.email} · {roles.join(", ")}
              </p>
            ) : null}
          </div>

          <button
            type="button"
            onClick={handleLogout}
            className="self-start rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10 lg:self-auto"
          >
            Cerrar sesión
          </button>
        </div>

        <nav className="flex flex-wrap gap-2">
          {visibleLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/admin"}
              className={({ isActive }) =>
                [
                  "rounded-full px-4 py-2 text-sm font-semibold transition",
                  isActive
                    ? "bg-blue-500 text-white shadow-lg shadow-blue-500/30"
                    : "bg-white/5 text-slate-200 hover:bg-white/10",
                ].join(" ")
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
}
