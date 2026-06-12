from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.pedido import Pedido


class Pago(SQLModel, table=True):
    __tablename__ = "pago"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id", index=True)
    monto: Decimal = Field(default=0, max_digits=10, decimal_places=2, ge=0)
    estado: str = Field(max_length=20)

    mp_preference_id: Optional[str] = Field(default=None, max_length=255)
    mp_init_point: Optional[str] = Field(default=None, max_length=500)
    mp_payment_id: Optional[int] = Field(default=None, sa_type=BigInteger)
    mp_merchant_order_id: Optional[int] = Field(default=None, sa_type=BigInteger)
    mp_status: Optional[str] = Field(default=None, max_length=50)
    mp_status_detail: Optional[str] = Field(default=None, max_length=100)
    transaction_amount: Decimal = Field(default=0, max_digits=10, decimal_places=2, ge=0)
    payment_method_id: Optional[str] = Field(default=None, max_length=50)
    external_reference: Optional[str] = Field(default=None, max_length=100, unique=True)

    idempotency_key: str = Field(max_length=100, unique=True)

    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None)

    pedido: "Pedido" = Relationship()