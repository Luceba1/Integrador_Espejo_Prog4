from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class UsuarioRol(SQLModel, table=True):
    __tablename__ = "usuario_rol"

    usuario_id: Optional[int] = Field(
        default=None,
        foreign_key="usuario.id",
        primary_key=True,
    )
    rol_id: Optional[int] = Field(
        default=None,
        foreign_key="rol.id",
        primary_key=True,
    )
    asignado_por_id: Optional[int] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
