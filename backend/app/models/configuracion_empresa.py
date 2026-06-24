from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class ConfiguracionEmpresa(SQLModel, table=True):
    __tablename__ = "configuracion_empresa"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre_empresa: str = Field(default="FoodStore", max_length=120)
    domicilio_retiro: Optional[str] = Field(default=None, max_length=255)
    banco: Optional[str] = Field(default=None, max_length=100)
    titular: Optional[str] = Field(default=None, max_length=120)
    cuit: Optional[str] = Field(default=None, max_length=30)
    cbu: Optional[str] = Field(default=None, max_length=40)
    alias: Optional[str] = Field(default=None, max_length=80)
    instrucciones_transferencia: Optional[str] = Field(default=None, max_length=500)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
