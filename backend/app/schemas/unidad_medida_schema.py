from datetime import datetime
from typing import Optional

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class UnidadMedidaCreate(SQLModel):
    nombre: str = Field(min_length=2, max_length=50)
    simbolo: str = Field(min_length=1, max_length=10)
    tipo: str = Field(min_length=2, max_length=20)
    activo: bool = True


class UnidadMedidaUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=50)
    simbolo: Optional[str] = Field(default=None, min_length=1, max_length=10)
    tipo: Optional[str] = Field(default=None, min_length=2, max_length=20)
    activo: Optional[bool] = None


class UnidadMedidaRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    simbolo: str
    tipo: str
    activo: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
