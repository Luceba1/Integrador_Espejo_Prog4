import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";

interface RoleGuardProps {
  roles: string[];
}

export default function RoleGuard({ roles }: RoleGuardProps) {
  const { hasRole, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-[55vh] items-center justify-center text-slate-300">
        Verificando permisos...
      </div>
    );
  }

  if (!hasRole(...roles)) {
    return <Navigate to="/sin-permisos" replace />;
  }

  return <Outlet />;
}
