from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, List

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.usuario import Usuario
    from app.models.pedido import Pedido


class DireccionEntrega(SQLModel, table=True):
    __tablename__ = "direccion_entrega"

    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    etiqueta: Optional[str] = Field(default=None, max_length=80)
    linea1: str = Field(min_length=3, max_length=255)
    linea2: Optional[str] = Field(default=None, max_length=255)
    ciudad: str = Field(min_length=2, max_length=100)
    latitud: Optional[Decimal] = Field(default=None, max_digits=9, decimal_places=6)
    longitud: Optional[Decimal] = Field(default=None, max_digits=9, decimal_places=6)
    es_principal: bool = Field(default=False)
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None)

    usuario: "Usuario" = Relationship(back_populates="direcciones")
    pedidos: List["Pedido"] = Relationship(back_populates="direccion")
