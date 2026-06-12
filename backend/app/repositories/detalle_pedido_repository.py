from sqlmodel import Session

from app.models.detalle_pedido import DetallePedido
from app.repositories.base_repository import BaseRepository


class DetallePedidoRepository(BaseRepository[DetallePedido]):
    def __init__(self, session: Session):
        super().__init__(session, DetallePedido)

    def update(self, entity: DetallePedido) -> DetallePedido:  # pragma: no cover
        raise RuntimeError("DetallePedido contiene snapshots y no debe editarse después de creado.")
