from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, List

from sqlmodel import Field, Relationship, SQLModel

from app.models.usuario_rol import UsuarioRol

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class Rol(SQLModel, table=True):
    __tablename__ = "rol"

    id: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, unique=True, min_length=2, max_length=30)
    nombre: str = Field(min_length=2, max_length=80)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None)

    usuarios: List["Usuario"] = Relationship(
        back_populates="roles",
        link_model=UsuarioRol,
    )
