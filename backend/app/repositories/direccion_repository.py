from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models.direccion_entrega import DireccionEntrega
from app.repositories.base_repository import BaseRepository


class DireccionRepository(BaseRepository[DireccionEntrega]):
    def __init__(self, session: Session):
        super().__init__(session, DireccionEntrega)

    def get_active_by_id_for_user(self, direccion_id: int, usuario_id: int) -> DireccionEntrega | None:
        statement = select(DireccionEntrega).where(
            DireccionEntrega.id == direccion_id,
            DireccionEntrega.usuario_id == usuario_id,
            DireccionEntrega.deleted_at.is_(None),
            DireccionEntrega.activo == True,  # noqa: E712
        )
        return self.session.exec(statement).first()

    def list_active_by_user(self, usuario_id: int) -> list[DireccionEntrega]:
        statement = (
            select(DireccionEntrega)
            .where(
                DireccionEntrega.usuario_id == usuario_id,
                DireccionEntrega.deleted_at.is_(None),
                DireccionEntrega.activo == True,  # noqa: E712
            )
            .order_by(DireccionEntrega.es_principal.desc(), DireccionEntrega.created_at.desc())
        )
        return list(self.session.exec(statement).all())

    def user_has_active_addresses(self, usuario_id: int) -> bool:
        statement = select(DireccionEntrega.id).where(
            DireccionEntrega.usuario_id == usuario_id,
            DireccionEntrega.deleted_at.is_(None),
            DireccionEntrega.activo == True,  # noqa: E712
        )
        return self.session.exec(statement).first() is not None

    def unset_principal_for_user(self, usuario_id: int) -> None:
        statement = select(DireccionEntrega).where(
            DireccionEntrega.usuario_id == usuario_id,
            DireccionEntrega.es_principal == True,  # noqa: E712
            DireccionEntrega.deleted_at.is_(None),
            DireccionEntrega.activo == True,  # noqa: E712
        )
        ahora = datetime.now(timezone.utc)
        for direccion in self.session.exec(statement).all():
            direccion.es_principal = False
            direccion.updated_at = ahora
            self.session.add(direccion)
        self.session.flush()

    def get_principal_by_user(self, usuario_id: int) -> DireccionEntrega | None:
        statement = select(DireccionEntrega).where(
            DireccionEntrega.usuario_id == usuario_id,
            DireccionEntrega.es_principal == True,  # noqa: E712
            DireccionEntrega.deleted_at.is_(None),
            DireccionEntrega.activo == True,  # noqa: E712
        )
        return self.session.exec(statement).first()
