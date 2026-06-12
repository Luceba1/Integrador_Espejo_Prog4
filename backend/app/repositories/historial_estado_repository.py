from sqlmodel import Session, select

from app.models.historial_estado_pedido import HistorialEstadoPedido
from app.repositories.base_repository import BaseRepository


class HistorialEstadoRepository(BaseRepository[HistorialEstadoPedido]):
    def __init__(self, session: Session):
        super().__init__(session, HistorialEstadoPedido)

    def list_by_pedido(self, pedido_id: int) -> list[HistorialEstadoPedido]:
        statement = (
            select(HistorialEstadoPedido)
            .where(HistorialEstadoPedido.pedido_id == pedido_id)
            .order_by(HistorialEstadoPedido.created_at.asc(), HistorialEstadoPedido.id.asc())
        )
        return list(self.session.exec(statement).all())

    def update(self, entity: HistorialEstadoPedido) -> HistorialEstadoPedido:  # pragma: no cover
        raise RuntimeError("HistorialEstadoPedido es append-only: no se permite UPDATE.")

    def hard_delete(self, entity: HistorialEstadoPedido) -> None:  # pragma: no cover
        raise RuntimeError("HistorialEstadoPedido es append-only: no se permite DELETE.")
