import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";
import { useCarrito } from "../../hooks/useCarrito";

const links = [
  { to: "/store", label: "Home store", end: true },
  { to: "/store/pedidos", label: "Mis pedidos" },
];

export default function StoreShell() {
  const { isAuthenticated, logout, usuario, roles, hasRole } = useAuth();
  const { totalItems } = useCarrito();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/store", { replace: true });
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-white/10 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="text-sm font-medium uppercase tracking-[0.25em] text-emerald-300">Store</p>
              <h1 className="text-2xl font-bold">Sistema de pedidos</h1>
              {isAuthenticated ? (
                <p className="mt-1 text-sm text-slate-400">
                  {usuario?.email} · {roles.join(", ")}
                </p>
              ) : (
                <p className="mt-1 text-sm text-slate-400">Catálogo público y carrito persistente.</p>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <Link
                to="/store/carrito"
                aria-label={`Abrir carrito con ${totalItems} producto${totalItems === 1 ? "" : "s"}`}
                className="relative inline-flex h-11 w-11 items-center justify-center rounded-full border border-white/10 bg-white/5 text-xl text-slate-100 transition hover:bg-white/10"
                title="Ver carrito"
              >
                🛒
                {totalItems > 0 ? (
                  <span className="absolute -right-1 -top-1 flex h-6 min-w-6 items-center justify-center rounded-full bg-emerald-500 px-1.5 text-xs font-bold text-white shadow-lg shadow-emerald-500/30">
                    {totalItems > 99 ? "99+" : totalItems}
                  </span>
                ) : null}
              </Link>

              {hasRole("ADMIN", "PEDIDOS", "STOCK") ? (
                <Link
                  to="/admin"
                  className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10"
                >
                  Administración
                </Link>
              ) : null}
              {isAuthenticated ? (
                <button
                  type="button"
                  onClick={handleLogout}
                  className="rounded-2xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:bg-white/10"
                >
                  Cerrar sesión
                </button>
              ) : (
                <Link
                  to="/login"
                  className="rounded-2xl bg-emerald-500 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-400"
                >
                  Iniciar sesión
                </Link>
              )}
            </div>
          </div>

          <nav className="flex flex-wrap gap-2">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.end}
                className={({ isActive }) =>
                  [
                    "rounded-full px-4 py-2 text-sm font-semibold transition",
                    isActive ? "bg-emerald-500 text-white shadow-lg shadow-emerald-500/30" : "bg-white/5 text-slate-200 hover:bg-white/10",
                  ].join(" ")
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}
