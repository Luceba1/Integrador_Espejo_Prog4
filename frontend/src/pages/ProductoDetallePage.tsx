import { Link, useParams } from "react-router-dom";

import PageContainer from "../components/layout/PageContainer";
import ProductoDetailCard from "../components/productos/ProductoDetailCard";
import { useProducto } from "../hooks/useProductos";

export default function ProductoDetallePage() {
  const params = useParams();
  const id = Number(params.id);
  const invalidId = !Number.isInteger(id) || id <= 0;

  const productoQuery = useProducto(id);

  return (
    <PageContainer
      title="Detalle de producto"
      subtitle="Ruta dinámica con useParams para mostrar un registro puntual."
      actions={
        <Link
          to="/admin/productos"
          className="rounded-2xl border border-white/10 px-4 py-3 font-semibold text-slate-100 hover:bg-white/10"
        >
          Volver a productos
        </Link>
      }
    >
      {invalidId ? (
        <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-rose-200">
          El identificador del producto no es válido.
        </div>
      ) : null}

      {!invalidId && productoQuery.isLoading ? (
        <div className="rounded-3xl border border-white/10 bg-white/5 p-8 text-slate-300">
          Cargando detalle...
        </div>
      ) : null}

      {!invalidId && productoQuery.isError ? (
        <div className="rounded-3xl border border-rose-500/30 bg-rose-500/10 p-8 text-rose-200">
          {productoQuery.error instanceof Error
            ? productoQuery.error.message
            : "No se pudo cargar el detalle del producto."}
        </div>
      ) : null}

      {!invalidId && productoQuery.data ? <ProductoDetailCard producto={productoQuery.data} /> : null}
    </PageContainer>
  );
}
