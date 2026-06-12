from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, Relationship, SQLModel

from app.models.producto_categoria import ProductoCategoria
from app.models.producto_ingrediente import ProductoIngrediente

if TYPE_CHECKING:
    from app.models.categoria import Categoria
    from app.models.ingrediente import Ingrediente
    from app.models.detalle_pedido import DetallePedido
    from app.models.unidad_medida import UnidadMedida


class Producto(SQLModel, table=True):
    __tablename__ = "producto"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, min_length=2, max_length=150)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    precio_base: Decimal = Field(default=0, max_digits=10, decimal_places=2, ge=0)
    unidad_venta_id: Optional[int] = Field(default=None, foreign_key="unidad_medida.id", index=True)
    imagenes_url: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    stock_cantidad: int = Field(default=0, ge=0)
    disponible: bool = Field(default=True)
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None)

    categorias: List["Categoria"] = Relationship(
        back_populates="productos",
        link_model=ProductoCategoria,
    )
    ingredientes: List["Ingrediente"] = Relationship(
        back_populates="productos",
        link_model=ProductoIngrediente,
    )
    unidad_venta: Optional["UnidadMedida"] = Relationship()
    detalles_pedido: List["DetallePedido"] = Relationship(back_populates="producto")