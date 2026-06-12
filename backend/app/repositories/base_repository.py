from datetime import datetime, timezone
from typing import Generic, TypeVar

from sqlmodel import Session, SQLModel, func, select

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: Session, model: type[ModelType]):
        self.session = session
        self.model = model

    def get_by_id(self, entity_id: int) -> ModelType | None:
        return self.session.get(self.model, entity_id)

    def list_all(self, skip: int = 0, limit: int | None = None) -> list[ModelType]:
        statement = select(self.model).offset(skip)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self.session.exec(statement).all())

    def count(self) -> int:
        statement = select(func.count()).select_from(self.model)
        return int(self.session.exec(statement).one())

    def create(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def update(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def soft_delete(self, entity: ModelType) -> None:
        if hasattr(entity, "activo"):
            setattr(entity, "activo", False)
        if hasattr(entity, "deleted_at"):
            setattr(entity, "deleted_at", datetime.now(timezone.utc))
        self.session.add(entity)
        self.session.flush()

    def hard_delete(self, entity: ModelType) -> None:
        self.session.delete(entity)
        self.session.flush()
