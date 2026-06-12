from typing import Optional

from sqlmodel import Session, select

from app.models.pago import Pago
from app.repositories.base_repository import BaseRepository


class PagoRepository(BaseRepository[Pago]):
    def __init__(self, session: Session):
        super().__init__(session, Pago)

    def get_by_pedido(self, pedido_id: int) -> list[Pago]:
        statement = (
            select(Pago)
            .where(Pago.pedido_id == pedido_id)
            .order_by(Pago.created_at.desc())
        )
        return list(self.session.exec(statement).all())

    def get_ultimo_by_pedido(self, pedido_id: int) -> Optional[Pago]:
        pagos = self.get_by_pedido(pedido_id)
        return pagos[0] if pagos else None

    def get_by_idempotency_key(self, key: str) -> Optional[Pago]:
        statement = select(Pago).where(Pago.idempotency_key == key)
        return self.session.exec(statement).first()

    def get_by_mp_payment_id(self, mp_payment_id: int) -> Optional[Pago]:
        statement = select(Pago).where(Pago.mp_payment_id == mp_payment_id)
        return self.session.exec(statement).first()

    def get_by_mp_merchant_order_id(self, merchant_order_id: int) -> Optional[Pago]:
        statement = select(Pago).where(Pago.mp_merchant_order_id == merchant_order_id)
        return self.session.exec(statement).first()