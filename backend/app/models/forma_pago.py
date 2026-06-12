from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class FormaPago(SQLModel, table=True):
    __tablename__ = "forma_pago"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True, min_length=2, max_length=40)
    nombre: str = Field(min_length=2, max_length=80)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None)
