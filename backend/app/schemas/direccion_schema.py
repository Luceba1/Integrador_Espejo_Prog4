from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class DireccionCreate(SQLModel):
    etiqueta: Optional[str] = Field(default=None, max_length=80)
    linea1: str = Field(min_length=3, max_length=255)
    linea2: Optional[str] = Field(default=None, max_length=255)
    ciudad: str = Field(min_length=2, max_length=100)
    latitud: Optional[Decimal] = Field(default=None, ge=-90, le=90)
    longitud: Optional[Decimal] = Field(default=None, ge=-180, le=180)
    es_principal: bool = False


class DireccionUpdate(SQLModel):
    etiqueta: Optional[str] = Field(default=None, max_length=80)
    linea1: Optional[str] = Field(default=None, min_length=3, max_length=255)
    linea2: Optional[str] = Field(default=None, max_length=255)
    ciudad: Optional[str] = Field(default=None, min_length=2, max_length=100)
    latitud: Optional[Decimal] = Field(default=None, ge=-90, le=90)
    longitud: Optional[Decimal] = Field(default=None, ge=-180, le=180)


class DireccionRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    etiqueta: Optional[str] = None
    linea1: str
    linea2: Optional[str] = None
    ciudad: str
    latitud: Optional[Decimal] = None
    longitud: Optional[Decimal] = None
    es_principal: bool
    activo: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
