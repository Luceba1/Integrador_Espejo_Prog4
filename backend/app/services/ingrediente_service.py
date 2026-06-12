from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.ingrediente import Ingrediente
from app.schemas.ingrediente_schema import IngredienteCreate, IngredienteUpdate
from app.uow.unit_of_work import SQLModelUnitOfWork


def _integrity_error(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
    )


def listar(uow: SQLModelUnitOfWork, incluir_eliminados: bool = False, page: int = 1, size: int = 50) -> list[Ingrediente]:
    return uow.ingredientes.list_paginated(incluir_eliminados=incluir_eliminados, page=page, size=size)


def obtener_por_id(uow: SQLModelUnitOfWork, ingrediente_id: int, incluir_eliminados: bool = False) -> Ingrediente:
    ingrediente = uow.ingredientes.get_by_id_with_unit(ingrediente_id) if incluir_eliminados else uow.ingredientes.get_active_by_id(ingrediente_id)
    if ingrediente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingrediente no encontrado.",
        )
    return ingrediente


def _validar_unidad_medida(uow: SQLModelUnitOfWork, unidad_medida_id: int | None) -> int | None:
    if unidad_medida_id is None:
        return None
    unidad = uow.unidades_medida.get_by_id(unidad_medida_id)
    if unidad is None or not unidad.activo or unidad.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La unidad de medida indicada no existe o está eliminada.")
    return unidad_medida_id


def crear(uow: SQLModelUnitOfWork, payload: IngredienteCreate) -> Ingrediente:
    data = payload.model_dump()
    data["unidad_medida_id"] = _validar_unidad_medida(uow, data.get("unidad_medida_id"))
    ingrediente = Ingrediente(**data)
    try:
        return uow.ingredientes.create(ingrediente)
    except IntegrityError as exc:
        raise _integrity_error("No se pudo crear el ingrediente.") from exc


def actualizar(
    uow: SQLModelUnitOfWork,
    ingrediente_id: int,
    payload: IngredienteUpdate,
) -> Ingrediente:
    ingrediente = obtener_por_id(uow, ingrediente_id)
    cambios = payload.model_dump(exclude_unset=True)

    if "unidad_medida_id" in cambios:
        cambios["unidad_medida_id"] = _validar_unidad_medida(uow, cambios["unidad_medida_id"])

    for campo, valor in cambios.items():
        setattr(ingrediente, campo, valor)

    ingrediente.updated_at = datetime.now(timezone.utc)

    try:
        return uow.ingredientes.update(ingrediente)
    except IntegrityError as exc:
        raise _integrity_error("No se pudo actualizar el ingrediente.") from exc


def eliminar(uow: SQLModelUnitOfWork, ingrediente_id: int) -> None:
    ingrediente = obtener_por_id(uow, ingrediente_id)

    ingrediente.activo = False
    ingrediente.deleted_at = datetime.now(timezone.utc)
    ingrediente.updated_at = ingrediente.deleted_at
    try:
        uow.ingredientes.update(ingrediente)
    except IntegrityError as exc:
        raise _integrity_error("No se pudo eliminar el ingrediente.") from exc


def activar(uow: SQLModelUnitOfWork, ingrediente_id: int) -> Ingrediente:
    ingrediente = obtener_por_id(uow, ingrediente_id, incluir_eliminados=True)
    ingrediente.activo = True
    ingrediente.deleted_at = None
    ingrediente.updated_at = datetime.now(timezone.utc)
    try:
        return uow.ingredientes.update(ingrediente)
    except IntegrityError as exc:
        raise _integrity_error("No se pudo activar el ingrediente.") from exc
