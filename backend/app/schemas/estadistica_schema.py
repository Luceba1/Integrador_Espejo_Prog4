from datetime import date
from decimal import Decimal

from sqlmodel import Field, SQLModel


class EstadisticasResumenResponse(SQLModel):
    ventas_hoy: Decimal
    ventas_periodo: Decimal
    ticket_promedio: Decimal
    pedidos_activos: int
    pedidos_confirmados: int
    productos_activos: int
    stock_critico: int


class VentasPeriodoItem(SQLModel):
    periodo: date
    label: str
    total_ventas: Decimal
    cantidad_pedidos: int


class ProductoTopItem(SQLModel):
    producto_id: int
    nombre: str
    cantidad_vendida: int
    ingresos: Decimal


class PedidosEstadoItem(SQLModel):
    estado_codigo: str
    cantidad: int


class IngresosFormaPagoItem(SQLModel):
    forma_pago_codigo: str
    total: Decimal
    cantidad_pedidos: int


class VentasPeriodoResponse(SQLModel):
    desde: date
    hasta: date
    agrupacion: str = Field(default="day")
    items: list[VentasPeriodoItem] = Field(default_factory=list)


class ProductosTopResponse(SQLModel):
    items: list[ProductoTopItem] = Field(default_factory=list)


class PedidosEstadoResponse(SQLModel):
    items: list[PedidosEstadoItem] = Field(default_factory=list)


class IngresosFormaPagoResponse(SQLModel):
    desde: date
    hasta: date
    items: list[IngresosFormaPagoItem] = Field(default_factory=list)
