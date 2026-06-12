from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.pedido import Pedido
    from app.models.usuario import Usuario


class HistorialEstadoPedido(SQLModel, table=True):
    __tablename__ = "historial_estado_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id", index=True)
    estado_desde: Optional[str] = Field(default=None, foreign_key="estado_pedido.codigo", max_length=40)
    estado_hacia: str = Field(foreign_key="estado_pedido.codigo", max_length=40)
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id", index=True)
    motivo: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    pedido: "Pedido" = Relationship(back_populates="historial_estados")
    usuario: "Usuario" = Relationship(back_populates="historial_estados")
