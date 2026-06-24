from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.categoria import Categoria
from app.schemas.categoria_schema import CategoriaCreate, CategoriaTreeRead, CategoriaUpdate
from app.uow.unit_of_work import SQLModelUnitOfWork


def _integrity_error(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
    )


def _validar_parent(uow: SQLModelUnitOfWork, parent_id: int | None, categoria_id: int | None = None) -> None:
    if parent_id is None:
        return

    if categoria_id is not None and parent_id == categoria_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Una categoría no puede ser padre de sí misma.",
        )

    parent = uow.categorias.get_active_by_id(parent_id)
    if parent is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La categoría padre no existe o está eliminada.",
        )

    # Evita ciclos: una categoría no puede elegir como padre a una de sus hijas,
    # nietas, etc. Ejemplo inválido: Bebidas → Sin alcohol → Sin gas → Bebidas.
    if categoria_id is not None:
        actual = parent
        while actual is not None:
            if actual.id == categoria_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede mover la categoría dentro de una de sus propias subcategorías.",
                )
            actual = uow.categorias.get_active_by_id(actual.parent_id) if actual.parent_id else None


def listar(
    uow: SQLModelUnitOfWork,
    parent_id: int | None = None,
    solo_raiz: bool = False,
    incluir_eliminadas: bool = False,
    page: int = 1,
    size: int = 50,
    search: str | None = None,
) -> list[Categoria]:
    return uow.categorias.list_paginated(
        parent_id=parent_id,
        solo_raiz=solo_raiz,
        incluir_eliminadas=incluir_eliminadas,
        page=page,
        size=size,
        search=search,
    )


def listar_arbol(uow: SQLModelUnitOfWork, incluir_eliminadas: bool = False) -> list[CategoriaTreeRead]:
    categorias = uow.categorias.list_all_without_pagination(incluir_eliminadas=incluir_eliminadas)
    por_parent: dict[int | None, list[Categoria]] = {}
    for categoria in categorias:
        por_parent.setdefault(categoria.parent_id, []).append(categoria)

    def construir(categoria: Categoria) -> CategoriaTreeRead:
        nodo = CategoriaTreeRead.model_validate(categoria)
        nodo.hijos = [construir(hijo) for hijo in por_parent.get(categoria.id, [])]
        return nodo

    return [construir(categoria) for categoria in por_parent.get(None, [])]


def obtener_por_id(uow: SQLModelUnitOfWork, categoria_id: int) -> Categoria:
    categoria = uow.categorias.get_active_by_id(categoria_id)
    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada.",
        )
    return categoria


def crear(uow: SQLModelUnitOfWork, payload: CategoriaCreate) -> Categoria:
    _validar_parent(uow, payload.parent_id)

    if uow.categorias.nombre_exists(payload.nombre):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una categoría activa con ese nombre.",
        )

    categoria = Categoria(**payload.model_dump())
    try:
        return uow.categorias.create(categoria)
    except IntegrityError as exc:
        raise _integrity_error("No se pudo crear la categoría.") from exc


def actualizar(
    uow: SQLModelUnitOfWork,
    categoria_id: int,
    payload: CategoriaUpdate,
) -> Categoria:
    categoria = obtener_por_id(uow, categoria_id)
    cambios = payload.model_dump(exclude_unset=True)

    if "parent_id" in cambios:
        _validar_parent(uow, cambios["parent_id"], categoria_id=categoria_id)
        categoria.parent_id = cambios["parent_id"]

    if "nombre" in cambios and cambios["nombre"] is not None:
        if uow.categorias.nombre_exists(cambios["nombre"], exclude_id=categoria_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una categoría activa con ese nombre.",
            )
        categoria.nombre = cambios["nombre"]

    if "descripcion" in cambios:
        categoria.descripcion = cambios["descripcion"]
    if "imagen_url" in cambios:
        categoria.imagen_url = cambios["imagen_url"]

    categoria.updated_at = datetime.now(timezone.utc)

    try:
        return uow.categorias.update(categoria)
    except IntegrityError as exc:
        raise _integrity_error("No se pudo actualizar la categoría.") from exc


def eliminar(uow: SQLModelUnitOfWork, categoria_id: int) -> None:
    categoria = obtener_por_id(uow, categoria_id)


    categoria.activo = False
    categoria.deleted_at = datetime.now(timezone.utc)
    categoria.updated_at = categoria.deleted_at
    try:
        uow.categorias.update(categoria)
    except IntegrityError as exc:
        raise _integrity_error("No se pudo eliminar la categoría.") from exc


def activar(uow: SQLModelUnitOfWork, categoria_id: int) -> Categoria:
    categoria = uow.categorias.get_by_id(categoria_id)
    if categoria is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada.")
    if categoria.parent_id is not None:
        _validar_parent(uow, categoria.parent_id, categoria_id=categoria_id)
    categoria.activo = True
    categoria.deleted_at = None
    categoria.updated_at = datetime.now(timezone.utc)
    try:
        return uow.categorias.update(categoria)
    except IntegrityError as exc:
        raise _integrity_error("No se pudo activar la categoría.") from exc
