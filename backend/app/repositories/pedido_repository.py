from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.pedido import Pedido
from app.repositories.base_repository import BaseRepository


class PedidoRepository(BaseRepository[Pedido]):
    def __init__(self, session: Session):
        super().__init__(session, Pedido)

    def get_active_with_details(self, pedido_id: int) -> Pedido | None:
        statement = (
            select(Pedido)
            .where(
                Pedido.id == pedido_id,
                Pedido.activo == True,  # noqa: E712
                Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
            .options(
                selectinload(Pedido.detalles),
                selectinload(Pedido.historial_estados),
                selectinload(Pedido.direccion),
                selectinload(Pedido.usuario),
            )
        )
        return self.session.exec(statement).first()

    def list_active_for_user(
        self,
        usuario_id: int,
        estado_codigo: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> list[Pedido]:
        statement = (
            select(Pedido)
            .where(
                Pedido.usuario_id == usuario_id,
                Pedido.activo == True,  # noqa: E712
                Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
            .options(
                selectinload(Pedido.detalles),
                selectinload(Pedido.historial_estados),
                selectinload(Pedido.direccion),
                selectinload(Pedido.usuario),
            )
        )
        if estado_codigo:
            statement = statement.where(Pedido.estado_codigo == estado_codigo)

        statement = (
            statement.order_by(Pedido.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        return list(self.session.exec(statement).all())

    def list_active_all(
        self,
        estado_codigo: str | None = None,
        usuario_id: int | None = None,
        page: int = 1,
        size: int = 10,
    ) -> list[Pedido]:
        statement = (
            select(Pedido)
            .where(
                Pedido.activo == True,  # noqa: E712
                Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
            .options(
                selectinload(Pedido.detalles),
                selectinload(Pedido.historial_estados),
                selectinload(Pedido.direccion),
                selectinload(Pedido.usuario),
            )
        )
        if estado_codigo:
            statement = statement.where(Pedido.estado_codigo == estado_codigo)
        if usuario_id:
            statement = statement.where(Pedido.usuario_id == usuario_id)

        statement = statement.order_by(Pedido.created_at.desc()).offset((page - 1) * size).limit(size)
        return list(self.session.exec(statement).all())
