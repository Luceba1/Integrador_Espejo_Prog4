import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";

import FormError from "../components/common/FormError";
import { useAuth } from "../hooks/useAuth";
import * as authService from "../services/authService";

export default function RegisterPage() {
  const navigate = useNavigate();
  const { isAuthenticated, refreshMe } = useAuth();
  const [email, setEmail] = useState("");
  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) return <Navigate to="/store" replace />;

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await authService.register({ email, nombre, apellido: apellido || null, password });
      await refreshMe();
      navigate("/store", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo registrar el usuario.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="w-full max-w-md rounded-3xl border border-white/10 bg-slate-950/80 p-8 shadow-2xl shadow-black/30">
        <p className="text-sm uppercase tracking-[0.3em] text-emerald-300">Store</p>
        <h1 className="mt-3 text-3xl font-bold text-white">Crear cuenta cliente</h1>
        <p className="mt-2 text-sm text-slate-300">El backend asigna automáticamente el rol CLIENT.</p>

        <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
          <FormError message={error} />
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" className="w-full rounded-2xl border border-white/10 bg-slate-900 px-4 py-3 text-white outline-none" required />
          <input value={nombre} onChange={(e) => setNombre(e.target.value)} placeholder="Nombre" className="w-full rounded-2xl border border-white/10 bg-slate-900 px-4 py-3 text-white outline-none" required />
          <input value={apellido} onChange={(e) => setApellido(e.target.value)} placeholder="Apellido" className="w-full rounded-2xl border border-white/10 bg-slate-900 px-4 py-3 text-white outline-none" />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Contraseña" className="w-full rounded-2xl border border-white/10 bg-slate-900 px-4 py-3 text-white outline-none" required />
          <button type="submit" disabled={loading} className="w-full rounded-2xl bg-emerald-500 px-4 py-3 font-semibold text-white hover:bg-emerald-400 disabled:opacity-60">
            {loading ? "Registrando..." : "Registrarme"}
          </button>
        </form>

        <p className="mt-5 text-center text-sm text-slate-400">
          ¿Ya tenés cuenta? <Link to="/login" className="font-semibold text-emerald-300 hover:text-emerald-200">Iniciar sesión</Link>
        </p>
      </div>
    </div>
  );
}
