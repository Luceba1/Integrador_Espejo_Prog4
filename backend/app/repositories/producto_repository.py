from sqlalchemy import delete, or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.producto import Producto
from app.models.producto_categoria import ProductoCategoria
from app.models.producto_ingrediente import ProductoIngrediente
from app.repositories.base_repository import BaseRepository


class ProductoRepository(BaseRepository[Producto]):
    def __init__(self, session: Session):
        super().__init__(session, Producto)


    def list_with_relations(
        self,
        search: str | None = None,
        categoria_id: int | None = None,
        disponible: bool | None = None,
        incluir_eliminados: bool = False,
        page: int = 1,
        size: int = 10,
    ) -> list[Producto]:
        statement = select(Producto).options(
            selectinload(Producto.categorias),
            selectinload(Producto.ingredientes),
            selectinload(Producto.unidad_venta),
        )

        if not incluir_eliminados:
            statement = statement.where(
                Producto.activo == True,  # noqa: E712
                Producto.deleted_at.is_(None),  # type: ignore[attr-defined]
            )

        if categoria_id is not None:
            statement = statement.join(ProductoCategoria).where(
                ProductoCategoria.categoria_id == categoria_id
            )

        if disponible is not None:
            statement = statement.where(Producto.disponible == disponible)

        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                or_(
                    Producto.nombre.ilike(pattern),
                    Producto.descripcion.ilike(pattern),
                )
            )

        statement = statement.order_by(Producto.id.desc()).offset((page - 1) * size).limit(size)
        return list(self.session.exec(statement).all())

    def get_with_relations_any_status(self, producto_id: int) -> Producto | None:
        statement = (
            select(Producto)
            .where(Producto.id == producto_id)
            .options(
                selectinload(Producto.categorias),
                selectinload(Producto.ingredientes),
                selectinload(Producto.unidad_venta),
            )
        )
        return self.session.exec(statement).first()

    def list_active_with_relations(
        self,
        search: str | None = None,
        categoria_id: int | None = None,
        disponible: bool | None = None,
        page: int = 1,
        size: int = 10,
    ) -> list[Producto]:
        statement = (
            select(Producto)
            .where(
                Producto.activo == True,  # noqa: E712
                Producto.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
            .options(
                selectinload(Producto.categorias),
                selectinload(Producto.ingredientes),
                selectinload(Producto.unidad_venta),
            )
        )

        if categoria_id is not None:
            statement = statement.join(ProductoCategoria).where(
                ProductoCategoria.categoria_id == categoria_id
            )

        if disponible is not None:
            statement = statement.where(Producto.disponible == disponible)

        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                or_(
                    Producto.nombre.ilike(pattern),
                    Producto.descripcion.ilike(pattern),
                )
            )

        statement = statement.order_by(Producto.id.desc()).offset((page - 1) * size).limit(size)
        return list(self.session.exec(statement).all())

    def get_active_with_relations(self, producto_id: int) -> Producto | None:
        statement = (
            select(Producto)
            .where(
                Producto.id == producto_id,
                Producto.activo == True,  # noqa: E712
                Producto.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
            .options(
                selectinload(Producto.categorias),
                selectinload(Producto.ingredientes),
                selectinload(Producto.unidad_venta),
            )
        )
        return self.session.exec(statement).first()


    def list_ingrediente_config(self, producto_id: int) -> list[ProductoIngrediente]:
        statement = select(ProductoIngrediente).where(ProductoIngrediente.producto_id == producto_id)
        return list(self.session.exec(statement).all())

    def replace_ingrediente_config(self, producto_id: int, configs: list[ProductoIngrediente]) -> None:
        self.session.exec(delete(ProductoIngrediente).where(ProductoIngrediente.producto_id == producto_id))
        self.session.flush()
        for config in configs:
            self.session.add(config)
        self.session.flush()
