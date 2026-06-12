from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class CategoriaCreate(SQLModel):
    parent_id: Optional[int] = Field(default=None, ge=1)
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    imagen_url: Optional[str] = Field(default=None, max_length=255)


class CategoriaUpdate(SQLModel):
    parent_id: Optional[int] = Field(default=None, ge=1)
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(default=None, max_length=255)
    imagen_url: Optional[str] = Field(default=None, max_length=255)


class CategoriaRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_id: Optional[int] = None
    nombre: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    activo: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class CategoriaSimpleRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_id: Optional[int] = None
    nombre: str
    imagen_url: Optional[str] = None
    created_at: datetime


class CategoriaTreeRead(CategoriaRead):
    hijos: list["CategoriaTreeRead"] = Field(default_factory=list)


CategoriaTreeRead.model_rebuild()
