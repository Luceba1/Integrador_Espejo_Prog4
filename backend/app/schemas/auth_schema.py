from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, EmailStr
from sqlmodel import Field, SQLModel


class RolRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str


class UsuarioRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    nombre: str
    apellido: Optional[str] = None
    roles: list[RolRead] = Field(default_factory=list)
    created_at: datetime


class UsuarioRegister(SQLModel):
    email: EmailStr
    nombre: str = Field(min_length=2, max_length=80)
    apellido: Optional[str] = Field(default=None, max_length=80)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(SQLModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshTokenRequest(SQLModel):
    refresh_token: Optional[str] = Field(default=None, max_length=256)


class LogoutRequest(SQLModel):
    refresh_token: Optional[str] = Field(default=None, max_length=256)


class AuthResponse(SQLModel):
    usuario: UsuarioRead
    roles: list[str]
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None


class TokenResponse(SQLModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    usuario: UsuarioRead
    roles: list[str] = Field(default_factory=list)
