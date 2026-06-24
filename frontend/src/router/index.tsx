import { Navigate, createBrowserRouter } from "react-router-dom";

import ProtectedRoute from "../components/auth/ProtectedRoute";
import RoleGuard from "../components/auth/RoleGuard";
import AppShell from "../components/layout/AppShell";
import AdminHomePage from "../pages/AdminHomePage";
import AdminUsuariosPage from "../pages/AdminUsuariosPage";
import EmpresaConfigPage from "../pages/EmpresaConfigPage";
import CajeroPedidosPage from "../pages/CajeroPedidosPage";
import CategoriasPage from "../pages/CategoriasPage";
import IngredientesPage from "../pages/IngredientesPage";
import LoginPage from "../pages/LoginPage";
import ProductoDetallePage from "../pages/ProductoDetallePage";
import ProductosPage from "../pages/ProductosPage";
import UnidadesMedidaPage from "../pages/UnidadesMedidaPage";
import SinPermisosPage from "../pages/SinPermisosPage";
import StoreShell from "../components/store/StoreShell";
import CarritoPage from "../pages/CarritoPage";
import CheckoutPage from "../pages/CheckoutPage";
import MisPedidosPage from "../pages/MisPedidosPage";
import RegisterPage from "../pages/RegisterPage";
import StoreHomePage from "../pages/StoreHomePage";
import StoreProductoDetallePage from "../pages/StoreProductoDetallePage";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  { path: "/register", element: <RegisterPage /> },
  {
    path: "/store",
    element: <StoreShell />,
    children: [
      { index: true, element: <StoreHomePage /> },
      { path: "productos/:id", element: <StoreProductoDetallePage /> },
      { path: "carrito", element: <CarritoPage /> },
      {
        element: <ProtectedRoute />,
        children: [
          { path: "checkout", element: <CheckoutPage /> },
          { path: "pedidos", element: <MisPedidosPage /> },
        ],
      },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        path: "/admin",
        element: <AppShell />,
        children: [
          { index: true, element: <AdminHomePage /> },
          {
            element: <RoleGuard roles={["ADMIN", "STOCK"]} />,
            children: [
              { path: "categorias", element: <CategoriasPage /> },
              { path: "ingredientes", element: <IngredientesPage /> },
              { path: "productos", element: <ProductosPage /> },
              { path: "productos/:id", element: <ProductoDetallePage /> },
              { path: "unidades-medida", element: <UnidadesMedidaPage /> },
            ],
          },
          {
            element: <RoleGuard roles={["ADMIN", "PEDIDOS"]} />,
            children: [{ path: "pedidos", element: <CajeroPedidosPage /> }],
          },
          {
            element: <RoleGuard roles={["ADMIN"]} />,
            children: [
              { path: "usuarios", element: <AdminUsuariosPage /> },
              { path: "empresa", element: <EmpresaConfigPage /> },
            ],
          },
          { path: "sin-permisos", element: <SinPermisosPage /> },
        ],
      },
      { path: "/sin-permisos", element: <SinPermisosPage /> },
    ],
  },
  { path: "/", element: <Navigate to="/store" replace /> },
  { path: "*", element: <Navigate to="/store" replace /> },
]);
