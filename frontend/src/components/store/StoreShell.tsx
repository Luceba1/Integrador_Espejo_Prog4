import { FormEvent, useEffect, useState } from "react";
import { Link, Outlet, useLocation, useNavigate, useSearchParams } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";
import { useCarrito } from "../../hooks/useCarrito";
import { useCatalogoWebSocket } from "../../hooks/useCatalogoWebSocket";

export default function StoreShell() {
  const { isAuthenticated, logout, usuario, roles, hasRole } = useAuth();
  const { totalItems } = useCarrito();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const [searchTerm, setSearchTerm] = useState(searchParams.get("q") ?? "");
  const [accountMenuOpen, setAccountMenuOpen] = useState(false);

  useCatalogoWebSocket();

  useEffect(() => {
    setSearchTerm(searchParams.get("q") ?? "");
  }, [searchParams]);

  useEffect(() => {
    setAccountMenuOpen(false);
  }, [location.pathname]);

  async function handleLogout() {
    await logout();
    setAccountMenuOpen(false);
    navigate("/store", { replace: true });
  }

  function handleSearchSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = searchTerm.trim();
    navigate(value ? `/store?q=${encodeURIComponent(value)}` : "/store");
  }

  const isAdminLike = hasRole("ADMIN", "PEDIDOS", "STOCK");
  const accountLabel = !isAuthenticated ? "Invitado" : hasRole("ADMIN") ? "Admin" : isAdminLike ? "Staff" : "Cliente";

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="sticky top-0 z-50 border-b border-white/10 bg-slate-950/95 shadow-2xl shadow-slate-950/40 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-3 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <Link to="/store" className="shrink-0 text-2xl font-black tracking-tight text-white transition hover:text-emerald-200">
            <span className="text-emerald-300">Food</span>Store
          </Link>

          <div className="flex w-full flex-col gap-3 lg:w-auto lg:flex-row lg:items-center lg:justify-end">
            <form className="flex min-w-0 flex-1 gap-2 lg:w-[460px] lg:flex-none" onSubmit={handleSearchSubmit}>
              <input
                value={searchTerm}
                onChange={(event) => setSearchTerm(event.target.value)}
                placeholder="Buscar productos"
                className="h-12 min-w-0 flex-1 rounded-2xl border border-white/10 bg-slate-900 px-4 text-sm text-white outline-none placeholder:text-slate-500 focus:border-emerald-400/60"
              />
              <button
                type="submit"
                aria-label="Buscar productos"
                title="Buscar"
                className="inline-flex h-12 w-12 items-center justify-center rounded-2xl border border-emerald-300/30 bg-emerald-500 text-xl font-semibold text-white shadow-lg shadow-emerald-500/20 transition hover:bg-emerald-400"
              >
                🔍
              </button>
            </form>

            <div className="flex flex-wrap items-center justify-end gap-2">
              <Link
                to="/store/carrito"
                aria-label={`Abrir carrito con ${totalItems} producto${totalItems === 1 ? "" : "s"}`}
                className="relative inline-flex h-12 items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 text-sm font-semibold text-slate-100 transition hover:bg-white/10"
                title="Ver carrito"
              >
                <span className="text-xl">🛒</span>
                <span>Carrito</span>
                {totalItems > 0 ? (
                  <span className="absolute -right-1 -top-1 flex h-6 min-w-6 items-center justify-center rounded-full bg-emerald-500 px-1.5 text-xs font-bold text-white shadow-lg shadow-emerald-500/30">
                    {totalItems > 99 ? "99+" : totalItems}
                  </span>
                ) : null}
              </Link>

              {isAuthenticated ? (
                <Link
                  to="/store/pedidos"
                  className="inline-flex h-12 items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 text-sm font-semibold text-slate-200 transition hover:bg-white/10"
                >
                  <span className="text-lg">📋</span>
                  <span>Mis pedidos</span>
                </Link>
              ) : null}

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
                  <span className="text-xs font-semibold uppercase tracking-wide text-emerald-200">{accountLabel}</span>
                </button>

                {accountMenuOpen ? (
                  <div className="absolute right-0 mt-2 w-56 overflow-hidden rounded-2xl border border-white/10 bg-slate-900 shadow-2xl shadow-slate-950/60" role="menu">
                    <div className="border-b border-white/10 px-4 py-3">
                      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-300">Cuenta</p>
                      <p className="mt-1 truncate text-sm text-slate-300">{usuario?.email ?? "Sin sesión iniciada"}</p>
                    </div>

                    {isAdminLike ? (
                      <Link
                        to="/admin"
                        className="block px-4 py-3 text-sm font-semibold text-slate-200 transition hover:bg-white/10"
                        role="menuitem"
                      >
                        Administración
                      </Link>
                    ) : null}

                    {isAuthenticated ? (
                      <button
                        type="button"
                        onClick={handleLogout}
                        className="block w-full px-4 py-3 text-left text-sm font-semibold text-slate-200 transition hover:bg-white/10"
                        role="menuitem"
                      >
                        Cerrar sesión
                      </button>
                    ) : (
                      <Link
                        to="/login"
                        className="block px-4 py-3 text-sm font-semibold text-slate-200 transition hover:bg-white/10"
                        role="menuitem"
                      >
                        Iniciar sesión
                      </Link>
                    )}
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}
