from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

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


def _calcular_precio_unitario(stock_cantidad: Decimal, precio_costo_total: Decimal) -> Decimal:
    stock = Decimal(stock_cantidad or 0)
    precio_total = Decimal(precio_costo_total or 0)
    if stock <= 0 or precio_total <= 0:
        return Decimal("0.00")
    return (precio_total / stock).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def _precio_por_unidad(ingrediente: Ingrediente) -> Decimal:
    unitario = Decimal(getattr(ingrediente, "precio_costo_unitario", 0) or 0)
    if unitario > 0:
        return unitario.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return _calcular_precio_unitario(ingrediente.stock_cantidad, ingrediente.precio_costo_total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _inyectar_precio_calculado(ingrediente: Ingrediente) -> Ingrediente:
    object.__setattr__(ingrediente, "precio_por_unidad", _precio_por_unidad(ingrediente))
    return ingrediente


def listar(
    uow: SQLModelUnitOfWork,
    incluir_eliminados: bool = False,
    page: int = 1,
    size: int = 50,
    search: str | None = None,
    es_alergeno: bool | None = None,
    unidad_medida_id: int | None = None,
) -> list[Ingrediente]:
    ingredientes = uow.ingredientes.list_paginated(
        incluir_eliminados=incluir_eliminados,
        page=page,
        size=size,
        search=search,
        es_alergeno=es_alergeno,
        unidad_medida_id=unidad_medida_id,
    )
    return [_inyectar_precio_calculado(ingrediente) for ingrediente in ingredientes]


def obtener_por_id(uow: SQLModelUnitOfWork, ingrediente_id: int, incluir_eliminados: bool = False) -> Ingrediente:
    ingrediente = uow.ingredientes.get_by_id_with_unit(ingrediente_id) if incluir_eliminados else uow.ingredientes.get_active_by_id(ingrediente_id)
    if ingrediente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingrediente no encontrado.",
        )
    return _inyectar_precio_calculado(ingrediente)


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
    data["precio_costo_unitario"] = _calcular_precio_unitario(data.get("stock_cantidad"), data.get("precio_costo_total"))
    ingrediente = Ingrediente(**data)
    try:
        return _inyectar_precio_calculado(uow.ingredientes.create(ingrediente))
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

    if "stock_cantidad" in cambios or "precio_costo_total" in cambios:
        ingrediente.precio_costo_unitario = _calcular_precio_unitario(
            ingrediente.stock_cantidad,
            ingrediente.precio_costo_total,
        )

    ingrediente.updated_at = datetime.now(timezone.utc)

    try:
        return _inyectar_precio_calculado(uow.ingredientes.update(ingrediente))
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
        return _inyectar_precio_calculado(uow.ingredientes.update(ingrediente))
    except IntegrityError as exc:
        raise _integrity_error("No se pudo activar el ingrediente.") from exc
