from datetime import datetime
from typing import Optional

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class ConfiguracionEmpresaUpdate(SQLModel):
    nombre_empresa: str = Field(default="FoodStore", min_length=2, max_length=120)
    domicilio_retiro: Optional[str] = Field(default=None, max_length=255)
    banco: Optional[str] = Field(default=None, max_length=100)
    titular: Optional[str] = Field(default=None, max_length=120)
    cuit: Optional[str] = Field(default=None, max_length=30)
    cbu: Optional[str] = Field(default=None, max_length=40)
    alias: Optional[str] = Field(default=None, max_length=80)
    instrucciones_transferencia: Optional[str] = Field(default=None, max_length=500)


class ConfiguracionEmpresaRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre_empresa: str
    domicilio_retiro: Optional[str] = None
    banco: Optional[str] = None
    titular: Optional[str] = None
    cuit: Optional[str] = None
    cbu: Optional[str] = None
    alias: Optional[str] = None
    instrucciones_transferencia: Optional[str] = None
    updated_at: datetime
