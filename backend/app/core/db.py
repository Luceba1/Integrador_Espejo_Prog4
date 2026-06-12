from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings
from app import models  # noqa: F401

settings = get_settings()
engine = create_engine(settings.DATABASE_URL, echo=settings.SQL_ECHO)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
