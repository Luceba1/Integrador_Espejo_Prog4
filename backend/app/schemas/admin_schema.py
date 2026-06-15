from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import ConfigDict, EmailStr
from sqlmodel import Field, SQLModel

from app.schemas.auth_schema import RolRead


class UsuarioAdminRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    nombre: str
    apellido: Optional[str] = None
    activo: bool
    roles: list[RolRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class UsuarioAdminUpdate(SQLModel):
    email: Optional[EmailStr] = None
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=80)
    apellido: Optional[str] = Field(default=None, max_length=80)
    activo: Optional[bool] = None


class UsuarioRolesUpdate(SQLModel):
    roles: list[str] = Field(min_length=1)


class DashboardEstadoPedido(SQLModel):
    estado_codigo: str
    total: int


class DashboardVentaFormaPago(SQLModel):
    forma_pago_codigo: str
    total_pedidos: int
    total_ventas: Decimal


class DashboardSerieDiaria(SQLModel):
    fecha: date
    label: str
    pedidos: int
    ventas: Decimal


class DashboardTopProducto(SQLModel):
    producto_id: int
    nombre: str
    unidades_vendidas: int
    total_vendido: Decimal


class DashboardIngredienteStockBajo(SQLModel):
    ingrediente_id: int
    nombre: str
    stock_cantidad: Decimal
    unidad_simbolo: Optional[str] = None


class DashboardMetricasRead(SQLModel):
    productos_activos: int
    ingredientes_activos: int
    usuarios_activos: int
    pedidos_activos: int
    pedidos_hoy: int
    pagos_aprobados: int
    pagos_rechazados: int
    stock_critico: int
    ventas_confirmadas: Decimal
    ventas_hoy: Decimal
    ticket_promedio: Decimal
    pedidos_por_estado: list[DashboardEstadoPedido] = Field(default_factory=list)
    ventas_por_forma_pago: list[DashboardVentaFormaPago] = Field(default_factory=list)
    pedidos_ultimos_7_dias: list[DashboardSerieDiaria] = Field(default_factory=list)
    top_productos: list[DashboardTopProducto] = Field(default_factory=list)
    ingredientes_stock_bajo: list[DashboardIngredienteStockBajo] = Field(default_factory=list)
