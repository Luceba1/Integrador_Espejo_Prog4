import { Link } from "react-router-dom";

export default function SinPermisosPage() {
  return (
    <div className="mx-auto max-w-2xl rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-center">
      <p className="text-sm uppercase tracking-[0.3em] text-rose-200">403</p>
      <h1 className="mt-2 text-3xl font-bold text-white">No tenés permisos</h1>
      <p className="mt-3 text-slate-300">
        Tu usuario está autenticado, pero el rol actual no permite acceder a esta pantalla.
      </p>
      <Link
        to="/admin"
        className="mt-6 inline-flex rounded-2xl bg-blue-500 px-4 py-3 font-semibold text-white hover:bg-blue-400"
      >
        Volver al inicio
      </Link>
    </div>
  );
}
