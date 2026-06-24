from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.unidad_medida import UnidadMedida
from app.schemas.unidad_medida_schema import UnidadMedidaCreate, UnidadMedidaUpdate
from app.uow.unit_of_work import SQLModelUnitOfWork


def _normalizar_simbolo(simbolo: str) -> str:
    return simbolo.strip()


def _normalizar_texto(valor: str) -> str:
    return valor.strip()


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unidad de medida no encontrada.")


def listar(
    uow: SQLModelUnitOfWork,
    incluir_eliminadas: bool = False,
    page: int = 1,
    size: int = 50,
    search: str | None = None,
    tipo: str | None = None,
) -> list[UnidadMedida]:
    return uow.unidades_medida.list_paginated(
        incluir_eliminadas=incluir_eliminadas,
        page=page,
        size=size,
        search=search,
        tipo=tipo,
    )


def obtener(uow: SQLModelUnitOfWork, unidad_id: int, incluir_eliminadas: bool = False) -> UnidadMedida:
    unidad = uow.unidades_medida.get_by_id(unidad_id)
    if unidad is None or (unidad.deleted_at is not None and not incluir_eliminadas):
        raise _not_found()
    return unidad


def crear(uow: SQLModelUnitOfWork, payload: UnidadMedidaCreate) -> UnidadMedida:
    unidad = UnidadMedida(
        nombre=_normalizar_texto(payload.nombre),
        simbolo=_normalizar_simbolo(payload.simbolo),
        tipo=_normalizar_texto(payload.tipo),
        activo=payload.activo,
    )
    try:
        return uow.unidades_medida.create(unidad)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una unidad de medida con ese nombre o símbolo.",
        ) from exc


def actualizar(uow: SQLModelUnitOfWork, unidad_id: int, payload: UnidadMedidaUpdate) -> UnidadMedida:
    unidad = obtener(uow, unidad_id)
    cambios = payload.model_dump(exclude_unset=True)

    if "nombre" in cambios and cambios["nombre"] is not None:
        unidad.nombre = _normalizar_texto(cambios["nombre"])
    if "simbolo" in cambios and cambios["simbolo"] is not None:
        unidad.simbolo = _normalizar_simbolo(cambios["simbolo"])
    if "tipo" in cambios and cambios["tipo"] is not None:
        unidad.tipo = _normalizar_texto(cambios["tipo"])
    if "activo" in cambios and cambios["activo"] is not None:
        unidad.activo = cambios["activo"]
        if unidad.activo:
            unidad.deleted_at = None

    unidad.updated_at = datetime.now(timezone.utc)

    try:
        return uow.unidades_medida.update(unidad)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una unidad de medida con ese nombre o símbolo.",
        ) from exc


def eliminar(uow: SQLModelUnitOfWork, unidad_id: int) -> None:
    unidad = obtener(uow, unidad_id)

    # No se borra físicamente porque puede estar referenciada por productos o ingredientes.
    unidad.activo = False
    unidad.deleted_at = datetime.now(timezone.utc)
    unidad.updated_at = unidad.deleted_at
    uow.unidades_medida.update(unidad)


def activar(uow: SQLModelUnitOfWork, unidad_id: int) -> UnidadMedida:
    unidad = obtener(uow, unidad_id, incluir_eliminadas=True)
    unidad.activo = True
    unidad.deleted_at = None
    unidad.updated_at = datetime.now(timezone.utc)
    try:
        return uow.unidades_medida.update(unidad)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo activar la unidad de medida.",
        ) from exc
