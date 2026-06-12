from typing import Optional

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class CrearPagoRequest(SQLModel):
    pedido_id: int = Field(..., description="ID del pedido a pagar")


class ConfirmarPagoRequest(SQLModel):
    pedido_id: int = Field(..., description="ID del pedido")
    payment_id: Optional[int] = Field(default=None, description="ID del pago en MercadoPago")


class PagoCrearResponse(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    pago_id: int
    preference_id: str
    init_point: Optional[str] = None
    sandbox_init_point: Optional[str] = None
    public_key: Optional[str] = None


class PagoEstadoResponse(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    estado: Optional[str] = None
    pedido_id: int
    pedido_estado: Optional[str] = None
