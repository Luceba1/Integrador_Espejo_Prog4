from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.rol import Rol
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.repositories.base_repository import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, session: Session):
        super().__init__(session, Usuario)

    def get_active_by_id(self, usuario_id: int) -> Usuario | None:
        statement = (
            select(Usuario)
            .where(
                Usuario.id == usuario_id,
                Usuario.activo == True,  # noqa: E712
                Usuario.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
            .options(selectinload(Usuario.roles))
        )
        return self.session.exec(statement).first()

    def get_by_id_with_roles(self, usuario_id: int) -> Usuario | None:
        statement = (
            select(Usuario)
            .where(Usuario.id == usuario_id)
            .options(selectinload(Usuario.roles))
        )
        return self.session.exec(statement).first()

    def get_active_by_email(self, email: str) -> Usuario | None:
        statement = (
            select(Usuario)
            .where(
                Usuario.email == email.lower().strip(),
                Usuario.activo == True,  # noqa: E712
                Usuario.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
            .options(selectinload(Usuario.roles))
        )
        return self.session.exec(statement).first()

    def get_by_email_any_status(self, email: str) -> Usuario | None:
        statement = (
            select(Usuario)
            .where(Usuario.email == email.lower().strip())
            .options(selectinload(Usuario.roles))
        )
        return self.session.exec(statement).first()

    def email_exists(self, email: str) -> bool:
        statement = select(Usuario.id).where(Usuario.email == email.lower().strip())
        return self.session.exec(statement).first() is not None

    def list_paginated_admin(
        self,
        rol_codigo: str | None = None,
        search: str | None = None,
        incluir_eliminados: bool = False,
        page: int = 1,
        size: int = 10,
    ) -> list[Usuario]:
        statement = select(Usuario).options(selectinload(Usuario.roles))

        if not incluir_eliminados:
            statement = statement.where(
                Usuario.activo == True,  # noqa: E712
                Usuario.deleted_at.is_(None),  # type: ignore[attr-defined]
            )

        if search:
            pattern = f"%{search.strip()}%"
            statement = statement.where(
                or_(
                    Usuario.email.ilike(pattern),
                    Usuario.nombre.ilike(pattern),
                    Usuario.apellido.ilike(pattern),
                )
            )

        if rol_codigo:
            statement = (
                statement.join(UsuarioRol, UsuarioRol.usuario_id == Usuario.id)
                .join(Rol, Rol.id == UsuarioRol.rol_id)
                .where(Rol.codigo == rol_codigo)
            )

        statement = statement.order_by(Usuario.id.desc()).offset((page - 1) * size).limit(size)
        return list(self.session.exec(statement).all())
