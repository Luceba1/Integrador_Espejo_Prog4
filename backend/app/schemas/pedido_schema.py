from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class PedidoItemCreate(SQLModel):
    producto_id: int = Field(ge=1)
    cantidad: int = Field(ge=1)
    personalizacion: Optional[dict[str, Any]] = None


class PedidoCreate(SQLModel):
    direccion_id: Optional[int] = Field(default=None, ge=1)
    forma_pago_codigo: str = Field(min_length=2, max_length=40)
    notas: Optional[str] = Field(default=None, max_length=500)
    descuento: Decimal = Field(default=0, max_digits=10, decimal_places=2, ge=0)
    costo_envio: Decimal = Field(default=0, max_digits=10, decimal_places=2, ge=0)
    items: list[PedidoItemCreate] = Field(min_length=1)


class PedidoEstadoUpdate(SQLModel):
    estado_codigo: str = Field(min_length=2, max_length=40)
    motivo: Optional[str] = Field(default=None, max_length=500)
    # Solo se usa desde el panel ADMIN/PEDIDOS al cancelar.
    # Permite decidir si se devuelven ingredientes al stock.
    recuperar_stock: bool = True


class PedidoCancelacion(SQLModel):
    motivo: Optional[str] = Field(default="Cancelado por el cliente", max_length=500)


class DetallePedidoRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    pedido_id: int
    producto_id: int
    cantidad: int
    nombre_producto_snap: str
    precio_unitario_snap: Decimal
    subtotal_snap: Decimal
    personalizacion: Optional[dict[str, Any]] = None
    created_at: datetime


class HistorialEstadoPedidoRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pedido_id: int
    estado_desde: Optional[str] = None
    estado_hacia: str
    usuario_id: Optional[int] = None
    motivo: Optional[str] = None
    created_at: datetime


class PedidoRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    direccion_id: Optional[int] = None
    estado_codigo: str
    forma_pago_codigo: str
    subtotal: Decimal
    descuento: Decimal
    costo_envio: Decimal
    total: Decimal
    notas: Optional[str] = None
    activo: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    detalles: list[DetallePedidoRead] = Field(default_factory=list)
    historial_estados: list[HistorialEstadoPedidoRead] = Field(default_factory=list)


class EstadoPedidoRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    orden: int
    permite_cancelacion_cliente: bool
    es_final: bool
    activo: bool


class FormaPagoRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool
