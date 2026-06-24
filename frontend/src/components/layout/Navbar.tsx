import { useEffect, useState } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";

interface NavItem {
  to: string;
  label: string;
  icon: string;
  roles?: string[];
}

const links: NavItem[] = [
  { to: "/admin", label: "Inicio", icon: "🏠" },
  { to: "/admin/productos", label: "Productos", icon: "🍔", roles: ["ADMIN", "STOCK"] },
  { to: "/admin/categorias", label: "Categorías", icon: "🗂️", roles: ["ADMIN", "STOCK"] },
  { to: "/admin/ingredientes", label: "Ingredientes", icon: "🧂", roles: ["ADMIN", "STOCK"] },
  { to: "/admin/unidades-medida", label: "Unidades", icon: "⚖️", roles: ["ADMIN", "STOCK"] },
  { to: "/admin/pedidos", label: "Pedidos", icon: "📋", roles: ["ADMIN", "PEDIDOS"] },
  { to: "/admin/usuarios", label: "Usuarios", icon: "👥", roles: ["ADMIN"] },
  { to: "/admin/empresa", label: "Empresa", icon: "🏢", roles: ["ADMIN"] },
];

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { hasRole, logout, roles, usuario } = useAuth();
  const [accountMenuOpen, setAccountMenuOpen] = useState(false);

  useEffect(() => {
    setAccountMenuOpen(false);
  }, [location.pathname]);

  async function handleLogout() {
    await logout();
    setAccountMenuOpen(false);
    navigate("/login", { replace: true });
  }

  const visibleLinks = links.filter((link) => !link.roles || hasRole(...link.roles));
  const roleLabel = hasRole("ADMIN") ? "Admin" : hasRole("PEDIDOS") ? "Pedidos" : hasRole("STOCK") ? "Stock" : "Cuenta";

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-slate-950/95 shadow-2xl shadow-slate-950/40 backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-3">
            <div>
              <NavLink to="/admin" className="text-2xl font-black tracking-tight text-white transition hover:text-emerald-200">
                <span className="text-emerald-300">Food</span>Store
              </NavLink>
              <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-slate-400">
                <span className="rounded-full border border-blue-400/25 bg-blue-500/10 px-2 py-0.5 font-semibold uppercase tracking-[0.18em] text-blue-200">
                  Administración
                </span>
                {usuario ? <span className="truncate">{usuario.email}</span> : null}
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 self-start lg:self-auto">
            <NavLink
              to="/store"
              className={({ isActive }) =>
                [
                  "inline-flex h-12 items-center gap-2 rounded-2xl border px-4 text-sm font-semibold transition",
                  isActive
                    ? "border-emerald-400 bg-emerald-500 text-white shadow-lg shadow-emerald-500/25"
                    : "border-white/10 bg-white/5 text-slate-200 hover:bg-white/10",
                ].join(" ")
              }
              title="Ir al store"
            >
              <span className="text-lg">🛒</span>
              <span>Store</span>
            </NavLink>

            <div className="relative">
              <button
                type="button"
                onClick={() => setAccountMenuOpen((open) => !open)}
                className="inline-flex h-12 min-w-[104px] items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 text-slate-100 transition hover:bg-white/10"
                aria-expanded={accountMenuOpen}
                aria-haspopup="menu"
                title="Cuenta"
              >
                <span className="text-xl leading-none">👤</span>
                <span className="text-xs font-semibold uppercase tracking-wide text-emerald-200">{roleLabel}</span>
              </button>

              {accountMenuOpen ? (
                <div className="absolute right-0 mt-2 w-60 overflow-hidden rounded-2xl border border-white/10 bg-slate-900 shadow-2xl shadow-slate-950/60" role="menu">
                  <div className="border-b border-white/10 px-4 py-3">
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-300">Cuenta</p>
                    <p className="mt-1 truncate text-sm text-slate-300">{usuario?.email ?? "Sin sesión iniciada"}</p>
                    <p className="mt-1 text-xs text-slate-500">{roles.join(", ")}</p>
                  </div>
                  <NavLink
                    to="/store"
                    className="block px-4 py-3 text-sm font-semibold text-slate-200 transition hover:bg-white/10"
                    role="menuitem"
                  >
                    Ir al Store
                  </NavLink>
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="block w-full px-4 py-3 text-left text-sm font-semibold text-slate-200 transition hover:bg-white/10"
                    role="menuitem"
                  >
                    Cerrar sesión
                  </button>
                </div>
              ) : null}
            </div>
          </div>
        </div>

        <nav className="flex flex-wrap gap-2">
          {visibleLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/admin"}
              className={({ isActive }) =>
                [
                  "inline-flex h-11 items-center gap-2 rounded-2xl border px-4 text-sm font-semibold transition",
                  isActive
                    ? "border-blue-400 bg-blue-500 text-white shadow-lg shadow-blue-500/30"
                    : "border-white/10 bg-white/5 text-slate-200 hover:bg-white/10",
                ].join(" ")
              }
            >
              <span className="text-base">{link.icon}</span>
              <span>{link.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
}
