from typing import Optional

from sqlmodel import Session, select

from app.models.refresh_token import RefreshToken
from app.repositories.base_repository import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: Session):
        super().__init__(session, RefreshToken)

    def get_by_token_hash(self, token_hash: str) -> Optional[RefreshToken]:
        statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        return self.session.exec(statement).first()
