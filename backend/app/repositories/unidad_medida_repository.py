from sqlmodel import Session, select

from app.models.unidad_medida import UnidadMedida
from app.repositories.base_repository import BaseRepository


class UnidadMedidaRepository(BaseRepository[UnidadMedida]):
    def __init__(self, session: Session):
        super().__init__(session, UnidadMedida)


    def list_paginated(self, incluir_eliminadas: bool = False, page: int = 1, size: int = 50) -> list[UnidadMedida]:
        statement = select(UnidadMedida)
        if not incluir_eliminadas:
            statement = statement.where(
                UnidadMedida.activo == True,  # noqa: E712
                UnidadMedida.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        statement = statement.order_by(UnidadMedida.nombre).offset((page - 1) * size).limit(size)
        return list(self.session.exec(statement).all())

    def list_all_ordered(self, incluir_eliminadas: bool = False) -> list[UnidadMedida]:
        statement = select(UnidadMedida)
        if not incluir_eliminadas:
            statement = statement.where(
                UnidadMedida.activo == True,  # noqa: E712
                UnidadMedida.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        statement = statement.order_by(UnidadMedida.nombre)
        return list(self.session.exec(statement).all())

    def get_by_simbolo(self, simbolo: str) -> UnidadMedida | None:
        statement = select(UnidadMedida).where(UnidadMedida.simbolo == simbolo)
        return self.session.exec(statement).first()

    def list_active(self) -> list[UnidadMedida]:
        statement = (
            select(UnidadMedida)
            .where(
                UnidadMedida.activo == True,  # noqa: E712
                UnidadMedida.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
            .order_by(UnidadMedida.nombre)
        )
        return list(self.session.exec(statement).all())
