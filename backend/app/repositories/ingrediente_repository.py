from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.ingrediente import Ingrediente
from app.models.producto_ingrediente import ProductoIngrediente
from app.repositories.base_repository import BaseRepository


class IngredienteRepository(BaseRepository[Ingrediente]):
    def __init__(self, session: Session):
        super().__init__(session, Ingrediente)


    def list_paginated(
        self,
        incluir_eliminados: bool = False,
        page: int = 1,
        size: int = 50,
        search: str | None = None,
        es_alergeno: bool | None = None,
        unidad_medida_id: int | None = None,
    ) -> list[Ingrediente]:
        statement = select(Ingrediente).options(selectinload(Ingrediente.unidad_medida))
        if not incluir_eliminados:
            statement = statement.where(
                Ingrediente.activo == True,  # noqa: E712
                Ingrediente.deleted_at.is_(None),  # type: ignore[attr-defined]
            )

        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                or_(
                    Ingrediente.nombre.ilike(pattern),
                    Ingrediente.descripcion.ilike(pattern),
                )
            )

        if es_alergeno is not None:
            statement = statement.where(Ingrediente.es_alergeno == es_alergeno)

        if unidad_medida_id is not None:
            statement = statement.where(Ingrediente.unidad_medida_id == unidad_medida_id)

        statement = statement.order_by(Ingrediente.nombre).offset((page - 1) * size).limit(size)
        return list(self.session.exec(statement).all())

    def list_all_with_units(self, incluir_eliminados: bool = False) -> list[Ingrediente]:
        statement = select(Ingrediente).options(selectinload(Ingrediente.unidad_medida))
        if not incluir_eliminados:
            statement = statement.where(
                Ingrediente.activo == True,  # noqa: E712
                Ingrediente.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        statement = statement.order_by(Ingrediente.nombre)
        return list(self.session.exec(statement).all())

    def get_by_id_with_unit(self, ingrediente_id: int) -> Ingrediente | None:
        statement = select(Ingrediente).where(Ingrediente.id == ingrediente_id).options(selectinload(Ingrediente.unidad_medida))
        return self.session.exec(statement).first()

    def list_active(self) -> list[Ingrediente]:
        statement = (
            select(Ingrediente)
            .where(
                Ingrediente.activo == True,  # noqa: E712
                Ingrediente.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
            .options(selectinload(Ingrediente.unidad_medida))
            .order_by(Ingrediente.nombre)
        )
        return list(self.session.exec(statement).all())

    def get_active_by_id(self, ingrediente_id: int) -> Ingrediente | None:
        statement = (
            select(Ingrediente)
            .where(
                Ingrediente.id == ingrediente_id,
                Ingrediente.activo == True,  # noqa: E712
                Ingrediente.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
            .options(selectinload(Ingrediente.unidad_medida))
        )
        return self.session.exec(statement).first()

    def get_active_by_ids(self, ingrediente_ids: list[int]) -> list[Ingrediente]:
        if not ingrediente_ids:
            return []
        statement = select(Ingrediente).options(selectinload(Ingrediente.unidad_medida)).where(
            Ingrediente.id.in_(ingrediente_ids),  # type: ignore[attr-defined]
            Ingrediente.activo == True,  # noqa: E712
            Ingrediente.deleted_at.is_(None),  # type: ignore[attr-defined]
        )
        return list(self.session.exec(statement).all())

    def has_productos(self, ingrediente_id: int) -> bool:
        statement = select(ProductoIngrediente).where(
            ProductoIngrediente.ingrediente_id == ingrediente_id
        )
        return self.session.exec(statement).first() is not None
