from sqlmodel import Session, select

from app.models.forma_pago import FormaPago
from app.repositories.base_repository import BaseRepository


class FormaPagoRepository(BaseRepository[FormaPago]):
    def __init__(self, session: Session):
        super().__init__(session, FormaPago)

    def get_by_codigo(self, codigo: str) -> FormaPago | None:
        statement = select(FormaPago).where(FormaPago.codigo == codigo)
        return self.session.exec(statement).first()

    def list_active(self) -> list[FormaPago]:
        statement = select(FormaPago).where(FormaPago.activo == True).order_by(FormaPago.nombre)  # noqa: E712
        return list(self.session.exec(statement).all())
