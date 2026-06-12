from sqlmodel import Session, select

from app.models.estado_pedido import EstadoPedido
from app.repositories.base_repository import BaseRepository


class EstadoPedidoRepository(BaseRepository[EstadoPedido]):
    def __init__(self, session: Session):
        super().__init__(session, EstadoPedido)

    def get_by_codigo(self, codigo: str) -> EstadoPedido | None:
        statement = select(EstadoPedido).where(EstadoPedido.codigo == codigo)
        return self.session.exec(statement).first()

    def list_active(self) -> list[EstadoPedido]:
        statement = select(EstadoPedido).where(EstadoPedido.activo == True).order_by(EstadoPedido.orden)  # noqa: E712
        return list(self.session.exec(statement).all())
