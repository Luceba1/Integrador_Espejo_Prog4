from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, List

from sqlmodel import Field, Relationship, SQLModel

from app.models.usuario_rol import UsuarioRol

if TYPE_CHECKING:
    from app.models.rol import Rol
    from app.models.direccion_entrega import DireccionEntrega
    from app.models.pedido import Pedido
    from app.models.historial_estado_pedido import HistorialEstadoPedido


class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, min_length=5, max_length=150)
    nombre: str = Field(min_length=2, max_length=80)
    apellido: Optional[str] = Field(default=None, max_length=80)
    celular: Optional[str] = Field(default=None, max_length=20)
    password_hash: str = Field(max_length=255)
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = Field(default=None)

    roles: List["Rol"] = Relationship(
        back_populates="usuarios",
        link_model=UsuarioRol,
    )
    direcciones: List["DireccionEntrega"] = Relationship(back_populates="usuario")
    pedidos: List["Pedido"] = Relationship(back_populates="usuario")
    historial_estados: List["HistorialEstadoPedido"] = Relationship(back_populates="usuario")
