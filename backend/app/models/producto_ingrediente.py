from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlmodel import Field, SQLModel


class ProductoIngrediente(SQLModel, table=True):
    __tablename__ = "producto_ingrediente"

    producto_id: Optional[int] = Field(
        default=None,
        foreign_key="producto.id",
        primary_key=True,
    )
    ingrediente_id: Optional[int] = Field(
        default=None,
        foreign_key="ingrediente.id",
        primary_key=True,
    )
    es_removible: bool = Field(default=True)
    cantidad: Decimal = Field(default=Decimal("1.000"), max_digits=10, decimal_places=3, gt=0)
    unidad_medida_id: Optional[int] = Field(default=None, foreign_key="unidad_medida.id", index=True)
