from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class EstadoPedido(SQLModel, table=True):
    __tablename__ = "estado_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True, min_length=2, max_length=40)
    nombre: str = Field(min_length=2, max_length=80)
    orden: int = Field(ge=1)
    permite_cancelacion_cliente: bool = Field(default=False)
    es_final: bool = Field(default=False)
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None)
