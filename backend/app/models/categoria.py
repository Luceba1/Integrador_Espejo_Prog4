from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, List

from sqlmodel import Field, Relationship, SQLModel

from app.models.producto_categoria import ProductoCategoria

if TYPE_CHECKING:
    from app.models.producto import Producto


class Categoria(SQLModel, table=True):
    __tablename__ = "categoria"

    id: Optional[int] = Field(default=None, primary_key=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="categoria.id")
    nombre: str = Field(index=True, unique=True, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    imagen_url: Optional[str] = Field(default=None, max_length=255)
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None)

    productos: List["Producto"] = Relationship(
        back_populates="categorias",
        link_model=ProductoCategoria,
    )