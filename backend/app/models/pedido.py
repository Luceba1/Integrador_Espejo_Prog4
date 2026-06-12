from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, List

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.detalle_pedido import DetallePedido
    from app.models.direccion_entrega import DireccionEntrega
    from app.models.historial_estado_pedido import HistorialEstadoPedido
    from app.models.usuario import Usuario


class Pedido(SQLModel, table=True):
    __tablename__ = "pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    direccion_id: Optional[int] = Field(default=None, foreign_key="direccion_entrega.id", index=True)
    estado_codigo: str = Field(default="PENDIENTE", foreign_key="estado_pedido.codigo", index=True, max_length=40)
    forma_pago_codigo: str = Field(foreign_key="forma_pago.codigo", index=True, max_length=40)

    subtotal: Decimal = Field(default=0, max_digits=10, decimal_places=2, ge=0)
    descuento: Decimal = Field(default=0, max_digits=10, decimal_places=2, ge=0)
    costo_envio: Decimal = Field(default=0, max_digits=10, decimal_places=2, ge=0)
    total: Decimal = Field(default=0, max_digits=10, decimal_places=2, ge=0)
    notas: Optional[str] = Field(default=None, max_length=500)

    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None)

    usuario: "Usuario" = Relationship(back_populates="pedidos")
    direccion: "DireccionEntrega" = Relationship(back_populates="pedidos")
    detalles: List["DetallePedido"] = Relationship(back_populates="pedido")
    historial_estados: List["HistorialEstadoPedido"] = Relationship(back_populates="pedido")
