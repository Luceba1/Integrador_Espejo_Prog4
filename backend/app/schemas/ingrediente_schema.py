from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

from app.schemas.unidad_medida_schema import UnidadMedidaRead


class IngredienteCreate(SQLModel):
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    es_alergeno: bool = Field(default=False)
    stock_cantidad: Decimal = Field(default=Decimal("0.000"), max_digits=12, decimal_places=3, ge=0)
    unidad_medida_id: Optional[int] = Field(default=None, ge=1)


class IngredienteUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    es_alergeno: Optional[bool] = None
    stock_cantidad: Optional[Decimal] = Field(default=None, max_digits=12, decimal_places=3, ge=0)
    unidad_medida_id: Optional[int] = Field(default=None, ge=1)


class IngredienteRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: Optional[str] = None
    es_alergeno: bool
    stock_cantidad: Decimal
    unidad_medida_id: Optional[int] = None
    unidad_medida: Optional[UnidadMedidaRead] = None
    activo: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class IngredienteSimpleRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    es_alergeno: bool
    stock_cantidad: Decimal
    unidad_medida_id: Optional[int] = None
    unidad_medida: Optional[UnidadMedidaRead] = None
    activo: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
