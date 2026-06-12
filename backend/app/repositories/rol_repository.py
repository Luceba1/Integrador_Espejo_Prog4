from sqlmodel import Session, select

from app.models.rol import Rol
from app.repositories.base_repository import BaseRepository


class RolRepository(BaseRepository[Rol]):
    def __init__(self, session: Session):
        super().__init__(session, Rol)

    def get_by_codigo(self, codigo: str) -> Rol | None:
        statement = select(Rol).where(
            Rol.codigo == codigo,
            Rol.activo == True,  # noqa: E712
            Rol.deleted_at.is_(None),  # type: ignore[attr-defined]
        )
        return self.session.exec(statement).first()

    def list_active(self) -> list[Rol]:
        statement = (
            select(Rol)
            .where(
                Rol.activo == True,  # noqa: E712
                Rol.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
            .order_by(Rol.codigo)
        )
        return list(self.session.exec(statement).all())
