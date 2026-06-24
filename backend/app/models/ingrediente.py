from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, List

from sqlmodel import Field, Relationship, SQLModel

from app.models.producto_ingrediente import ProductoIngrediente

if TYPE_CHECKING:
    from app.models.producto import Producto
    from app.models.unidad_medida import UnidadMedida


class Ingrediente(SQLModel, table=True):
    __tablename__ = "ingrediente"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    es_alergeno: bool = Field(default=False)
    stock_cantidad: Decimal = Field(default=Decimal("0.000"), max_digits=12, decimal_places=3, ge=0)
    precio_costo_total: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2, ge=0)
    precio_costo_unitario: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=4, ge=0)
    unidad_medida_id: Optional[int] = Field(default=None, foreign_key="unidad_medida.id", index=True)
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None)

    unidad_medida: Optional["UnidadMedida"] = Relationship()
    productos: List["Producto"] = Relationship(
        back_populates="ingredientes",
        link_model=ProductoIngrediente,
    )
