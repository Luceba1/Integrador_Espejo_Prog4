from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, Any

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.pedido import Pedido
    from app.models.producto import Producto


class DetallePedido(SQLModel, table=True):
    __tablename__ = "detalle_pedido"

    pedido_id: int = Field(foreign_key="pedido.id", primary_key=True)
    producto_id: int = Field(foreign_key="producto.id", primary_key=True)
    cantidad: int = Field(ge=1)

    nombre_producto_snap: str = Field(max_length=150)
    precio_unitario_snap: Decimal = Field(default=0, max_digits=10, decimal_places=2, ge=0)
    subtotal_snap: Decimal = Field(default=0, max_digits=10, decimal_places=2, ge=0)
    personalizacion: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    pedido: "Pedido" = Relationship(back_populates="detalles")
    producto: "Producto" = Relationship(back_populates="detalles_pedido")
