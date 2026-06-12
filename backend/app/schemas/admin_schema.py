from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, EmailStr
from sqlmodel import Field, SQLModel

from app.schemas.auth_schema import RolRead


class UsuarioAdminRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    nombre: str
    apellido: Optional[str] = None
    activo: bool
    roles: list[RolRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class UsuarioAdminUpdate(SQLModel):
    email: Optional[EmailStr] = None
    nombre: Optional[str] = Field(default=None, min_length=2, max_length=80)
    apellido: Optional[str] = Field(default=None, max_length=80)
    activo: Optional[bool] = None


class UsuarioRolesUpdate(SQLModel):
    roles: list[str] = Field(min_length=1)
