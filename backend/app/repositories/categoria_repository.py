from sqlalchemy import func
from sqlmodel import Session, select

from app.models.categoria import Categoria
from app.models.producto import Producto
from app.models.producto_categoria import ProductoCategoria
from app.repositories.base_repository import BaseRepository


class CategoriaRepository(BaseRepository[Categoria]):
    def __init__(self, session: Session):
        super().__init__(session, Categoria)


    def list_paginated(
        self,
        parent_id: int | None = None,
        solo_raiz: bool = False,
        incluir_eliminadas: bool = False,
        page: int = 1,
        size: int = 50,
    ) -> list[Categoria]:
        statement = select(Categoria)

        if not incluir_eliminadas:
            statement = statement.where(
                Categoria.activo == True,  # noqa: E712
                Categoria.deleted_at.is_(None),  # type: ignore[attr-defined]
            )

        if parent_id is not None:
            statement = statement.where(Categoria.parent_id == parent_id)
        elif solo_raiz:
            statement = statement.where(Categoria.parent_id.is_(None))  # type: ignore[attr-defined]

        statement = statement.order_by(Categoria.parent_id, Categoria.nombre).offset((page - 1) * size).limit(size)
        return list(self.session.exec(statement).all())

    def list_all_without_pagination(self, incluir_eliminadas: bool = False) -> list[Categoria]:
        statement = select(Categoria)
        if not incluir_eliminadas:
            statement = statement.where(
                Categoria.activo == True,  # noqa: E712
                Categoria.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        statement = statement.order_by(Categoria.parent_id, Categoria.nombre)
        return list(self.session.exec(statement).all())

    def list_active(
        self,
        parent_id: int | None = None,
        solo_raiz: bool = False,
        page: int = 1,
        size: int = 50,
    ) -> list[Categoria]:
        statement = select(Categoria).where(
            Categoria.activo == True,  # noqa: E712
            Categoria.deleted_at.is_(None),  # type: ignore[attr-defined]
        )

        if parent_id is not None:
            statement = statement.where(Categoria.parent_id == parent_id)
        elif solo_raiz:
            statement = statement.where(Categoria.parent_id.is_(None))  # type: ignore[attr-defined]

        statement = statement.order_by(Categoria.nombre).offset((page - 1) * size).limit(size)
        return list(self.session.exec(statement).all())

    def list_all_active_without_pagination(self) -> list[Categoria]:
        statement = (
            select(Categoria)
            .where(
                Categoria.activo == True,  # noqa: E712
                Categoria.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
            .order_by(Categoria.parent_id, Categoria.nombre)
        )
        return list(self.session.exec(statement).all())

    def get_active_by_id(self, categoria_id: int) -> Categoria | None:
        categoria = self.get_by_id(categoria_id)
        if categoria is None or not categoria.activo or categoria.deleted_at is not None:
            return None
        return categoria

    def get_active_by_ids(self, categoria_ids: list[int]) -> list[Categoria]:
        if not categoria_ids:
            return []
        statement = select(Categoria).where(
            Categoria.id.in_(categoria_ids),  # type: ignore[attr-defined]
            Categoria.activo == True,  # noqa: E712
            Categoria.deleted_at.is_(None),  # type: ignore[attr-defined]
        )
        return list(self.session.exec(statement).all())

    def nombre_exists(self, nombre: str, exclude_id: int | None = None) -> bool:
        statement = select(Categoria).where(
            func.lower(Categoria.nombre) == nombre.lower(),
            Categoria.activo == True,  # noqa: E712
            Categoria.deleted_at.is_(None),  # type: ignore[attr-defined]
        )
        if exclude_id is not None:
            statement = statement.where(Categoria.id != exclude_id)
        return self.session.exec(statement).first() is not None

    def has_productos_activos(self, categoria_id: int) -> bool:
        statement = (
            select(Producto.id)
            .join(ProductoCategoria, ProductoCategoria.producto_id == Producto.id)
            .where(
                ProductoCategoria.categoria_id == categoria_id,
                Producto.activo == True,  # noqa: E712
                Producto.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        return self.session.exec(statement).first() is not None

    def has_subcategorias_activas(self, categoria_id: int) -> bool:
        statement = select(Categoria.id).where(
            Categoria.parent_id == categoria_id,
            Categoria.activo == True,  # noqa: E712
            Categoria.deleted_at.is_(None),  # type: ignore[attr-defined]
        )
        return self.session.exec(statement).first() is not None
