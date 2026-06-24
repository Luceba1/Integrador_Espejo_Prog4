from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

from app.schemas.categoria_schema import CategoriaSimpleRead
from app.schemas.ingrediente_schema import IngredienteSimpleRead
from app.schemas.unidad_medida_schema import UnidadMedidaRead


class ProductoIngredientePayload(SQLModel):
    ingrediente_id: int = Field(ge=1)
    cantidad: Decimal = Field(default=Decimal("1.000"), max_digits=10, decimal_places=3, gt=0)
    unidad_medida_id: Optional[int] = Field(default=None, ge=1)
    es_removible: bool = Field(default=True)


class ProductoCreate(SQLModel):
    nombre: str = Field(min_length=2, max_length=120)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    precio_base: Decimal = Field(default=0, max_digits=10, decimal_places=2, ge=0)
    margen_ganancia_porcentaje: Decimal = Field(default=Decimal("0.00"), max_digits=6, decimal_places=2, ge=0)
    unidad_venta_id: Optional[int] = Field(default=None, ge=1)
    imagenes_url: list[str] = Field(default_factory=list)
    # Se conserva por compatibilidad con la BD anterior, pero el stock real se calcula desde ingredientes.
    stock_cantidad: int = Field(default=0, ge=0)
    disponible: bool = Field(default=True)
    categoria_ids: list[int] = Field(default_factory=list)
    ingrediente_ids: list[int] = Field(default_factory=list)
    ingredientes_configurados: list[ProductoIngredientePayload] = Field(default_factory=list)


class ProductoUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=120)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    precio_base: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2, ge=0)
    margen_ganancia_porcentaje: Optional[Decimal] = Field(default=None, max_digits=6, decimal_places=2, ge=0)
    unidad_venta_id: Optional[int] = Field(default=None, ge=1)
    imagenes_url: Optional[list[str]] = None
    stock_cantidad: Optional[int] = Field(default=None, ge=0)
    disponible: Optional[bool] = None
    categoria_ids: Optional[list[int]] = None
    ingrediente_ids: Optional[list[int]] = None
    ingredientes_configurados: Optional[list[ProductoIngredientePayload]] = None


class ImagenProductoUpdate(SQLModel):
    imagenes_url: list[str] = Field(default_factory=list)


class ProductoDisponibilidadUpdate(SQLModel):
    disponible: bool


class ProductoStockUpdate(SQLModel):
    stock_cantidad: int = Field(ge=0)


class ProductoIngredienteRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    ingrediente_id: int
    ingrediente: Optional[IngredienteSimpleRead] = None
    cantidad: Decimal
    unidad_medida_id: Optional[int] = None
    unidad_medida: Optional[UnidadMedidaRead] = None
    es_removible: bool


class ProductoRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio_base: Decimal
    margen_ganancia_porcentaje: Decimal
    costo_ingredientes: Decimal = Decimal("0.00")
    precio_sugerido: Decimal = Decimal("0.00")
    unidad_venta_id: Optional[int] = None
    unidad_venta: Optional[UnidadMedidaRead] = None
    imagenes_url: list[str] = Field(default_factory=list)
    stock_cantidad: int
    disponible: bool
    activo: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class ProductoReadDetail(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio_base: Decimal
    margen_ganancia_porcentaje: Decimal
    costo_ingredientes: Decimal = Decimal("0.00")
    precio_sugerido: Decimal = Decimal("0.00")
    unidad_venta_id: Optional[int] = None
    unidad_venta: Optional[UnidadMedidaRead] = None
    imagenes_url: list[str] = Field(default_factory=list)
    # stock_cantidad queda como stock calculado: cuántas unidades del producto se pueden preparar con los ingredientes existentes.
    stock_cantidad: int
    disponible: bool
    activo: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    categorias: list[CategoriaSimpleRead] = Field(default_factory=list)
    ingredientes: list[IngredienteSimpleRead] = Field(default_factory=list)
    ingredientes_configurados: list[ProductoIngredienteRead] = Field(default_factory=list)


ProductoReadDetail.model_rebuild()
