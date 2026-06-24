from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP
from types import SimpleNamespace

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.categoria import Categoria
from app.models.ingrediente import Ingrediente
from app.models.producto import Producto
from app.models.producto_ingrediente import ProductoIngrediente
from app.schemas.producto_schema import ProductoCreate, ProductoIngredientePayload, ProductoUpdate
from app.uow.unit_of_work import SQLModelUnitOfWork


def _precio_por_unidad_ingrediente(ingrediente: Ingrediente) -> Decimal:
    unitario = Decimal(getattr(ingrediente, "precio_costo_unitario", 0) or 0)
    if unitario > 0:
        return unitario
    stock = Decimal(ingrediente.stock_cantidad or 0)
    precio_total = Decimal(getattr(ingrediente, "precio_costo_total", 0) or 0)
    if stock <= 0 or precio_total <= 0:
        return Decimal("0.00")
    return precio_total / stock


def _costo_config_ingrediente(ingrediente: Ingrediente | None, cantidad: Decimal) -> Decimal:
    if ingrediente is None or cantidad <= 0:
        return Decimal("0.00")
    return _precio_por_unidad_ingrediente(ingrediente) * Decimal(cantidad)


def _calcular_costos_producto(uow: SQLModelUnitOfWork, producto_id: int, margen_porcentaje: Decimal) -> tuple[Decimal, Decimal]:
    costo = Decimal("0.00")
    for config in uow.productos.list_ingrediente_config(producto_id):
        ingrediente = uow.ingredientes.get_active_by_id(config.ingrediente_id)
        costo += _costo_config_ingrediente(ingrediente, Decimal(config.cantidad or 0))
    costo = costo.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    margen = Decimal(margen_porcentaje or 0)
    precio_sugerido = (costo * (Decimal("1") + (margen / Decimal("100")))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return costo, precio_sugerido


def _integrity_error(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _validar_ids_unicos(ids: list[int], nombre_campo: str) -> None:
    if len(ids) != len(set(ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"No se permiten ids repetidos en {nombre_campo}.")


def _validar_unidad_venta(uow: SQLModelUnitOfWork, unidad_venta_id: int | None) -> int | None:
    if unidad_venta_id is None:
        return None
    unidad = uow.unidades_medida.get_by_id(unidad_venta_id)
    if unidad is None or not unidad.activo or unidad.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La unidad indicada no existe o está eliminada.")
    return unidad_venta_id


def _categoria_tiene_hijos(uow: SQLModelUnitOfWork, categoria_id: int) -> bool:
    return uow.categorias.has_subcategorias_activas(categoria_id)


def _expandir_hojas_con_padres(uow: SQLModelUnitOfWork, categoria_ids: list[int]) -> list[Categoria]:
    """Solo permite elegir hojas, pero guarda también los padres para conservar la jerarquía."""
    if not categoria_ids:
        return []
    _validar_ids_unicos(categoria_ids, "categoria_ids")

    seleccionadas = uow.categorias.get_active_by_ids(categoria_ids)
    if len(seleccionadas) != len(categoria_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Una o más categorías no existen o están eliminadas.")

    for categoria in seleccionadas:
        if _categoria_tiene_hijos(uow, categoria.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'La categoría "{categoria.nombre}" tiene subcategorías. Seleccioná una categoría final de la rama.',
            )

    todas: dict[int, Categoria] = {}
    for categoria in seleccionadas:
        actual: Categoria | None = categoria
        while actual is not None:
            todas[actual.id] = actual
            if actual.parent_id is None:
                break
            actual = uow.categorias.get_active_by_id(actual.parent_id)
    return list(todas.values())


def _normalizar_config_ingredientes(payload: ProductoCreate | ProductoUpdate) -> list[ProductoIngredientePayload]:
    configs = getattr(payload, "ingredientes_configurados", None)
    if configs:
        return list(configs)
    ingrediente_ids = getattr(payload, "ingrediente_ids", None) or []
    return [ProductoIngredientePayload(ingrediente_id=ingrediente_id) for ingrediente_id in ingrediente_ids]


def _validar_config_ingredientes(uow: SQLModelUnitOfWork, configs: list[ProductoIngredientePayload]) -> list[ProductoIngredientePayload]:
    if not configs:
        return []
    ids = [config.ingrediente_id for config in configs]
    _validar_ids_unicos(ids, "ingredientes_configurados.ingrediente_id")
    ingredientes = uow.ingredientes.get_active_by_ids(ids)
    if len(ingredientes) != len(ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uno o más ingredientes no existen.")
    for config in configs:
        if config.unidad_medida_id is not None:
            _validar_unidad_venta(uow, config.unidad_medida_id)
    return configs


def _aplicar_config_ingredientes(uow: SQLModelUnitOfWork, producto_id: int, configs: list[ProductoIngredientePayload]) -> None:
    links = [
        ProductoIngrediente(
            producto_id=producto_id,
            ingrediente_id=config.ingrediente_id,
            cantidad=config.cantidad,
            unidad_medida_id=config.unidad_medida_id,
            es_removible=config.es_removible,
        )
        for config in configs
    ]
    uow.productos.replace_ingrediente_config(producto_id, links)


def _stock_calculado(uow: SQLModelUnitOfWork, producto_id: int) -> int:
    configs = uow.productos.list_ingrediente_config(producto_id)
    if not configs:
        return 0
    posibles: list[int] = []
    for config in configs:
        ingrediente = uow.ingredientes.get_active_by_id(config.ingrediente_id)
        if ingrediente is None or config.cantidad <= 0:
            return 0
        disponibles = (Decimal(ingrediente.stock_cantidad) / Decimal(config.cantidad)).to_integral_value(rounding=ROUND_FLOOR)
        posibles.append(max(0, int(disponibles)))
    return min(posibles) if posibles else 0


def _inyectar_info_calculada(uow: SQLModelUnitOfWork, producto: Producto) -> Producto:
    producto.stock_cantidad = _stock_calculado(uow, producto.id)
    configuraciones = []
    for config in uow.productos.list_ingrediente_config(producto.id):
        ingrediente = uow.ingredientes.get_active_by_id(config.ingrediente_id)
        unidad = uow.unidades_medida.get_by_id(config.unidad_medida_id) if config.unidad_medida_id else None
        configuraciones.append(
            SimpleNamespace(
                ingrediente_id=config.ingrediente_id,
                ingrediente=(SimpleNamespace(
                    **ingrediente.model_dump(),
                    unidad_medida=ingrediente.unidad_medida,
                    precio_por_unidad=_precio_por_unidad_ingrediente(ingrediente).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                ) if ingrediente else None),
                cantidad=config.cantidad,
                unidad_medida_id=config.unidad_medida_id,
                unidad_medida=unidad,
                es_removible=config.es_removible,
            )
        )
    costo_ingredientes, precio_sugerido = _calcular_costos_producto(uow, producto.id, Decimal(producto.margen_ganancia_porcentaje or 0))
    object.__setattr__(producto, "costo_ingredientes", costo_ingredientes)
    object.__setattr__(producto, "precio_sugerido", precio_sugerido)
    object.__setattr__(producto, "ingredientes_configurados", configuraciones)
    return producto


def _cargar_relaciones(uow: SQLModelUnitOfWork, producto_id: int, incluir_eliminados: bool = False) -> Producto:
    producto = uow.productos.get_with_relations_any_status(producto_id) if incluir_eliminados else uow.productos.get_active_with_relations(producto_id)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado.")
    return _inyectar_info_calculada(uow, producto)


def listar(
    uow: SQLModelUnitOfWork,
    search: str | None = None,
    categoria_id: int | None = None,
    disponible: bool | None = None,
    incluir_eliminados: bool = False,
    page: int = 1,
    size: int = 10,
) -> list[Producto]:
    productos = uow.productos.list_with_relations(
        search=search,
        categoria_id=categoria_id,
        disponible=disponible,
        incluir_eliminados=incluir_eliminados,
        page=page,
        size=size,
    )
    return [_inyectar_info_calculada(uow, producto) for producto in productos]


def obtener_por_id(uow: SQLModelUnitOfWork, producto_id: int) -> Producto:
    return _cargar_relaciones(uow, producto_id)


def crear(uow: SQLModelUnitOfWork, payload: ProductoCreate) -> Producto:
    categorias = _expandir_hojas_con_padres(uow, payload.categoria_ids)
    configs = _validar_config_ingredientes(uow, _normalizar_config_ingredientes(payload))

    producto = Producto(
        nombre=payload.nombre,
        descripcion=payload.descripcion,
        precio_base=payload.precio_base,
        margen_ganancia_porcentaje=payload.margen_ganancia_porcentaje,
        unidad_venta_id=_validar_unidad_venta(uow, payload.unidad_venta_id),
        imagenes_url=payload.imagenes_url,
        stock_cantidad=0,
        disponible=payload.disponible,
    )
    producto.categorias = categorias

    try:
        producto = uow.productos.create(producto)
        _aplicar_config_ingredientes(uow, producto.id, configs)
    except IntegrityError as exc:
        raise _integrity_error("No se pudo crear el producto.") from exc

    return _cargar_relaciones(uow, producto.id)


def actualizar(uow: SQLModelUnitOfWork, producto_id: int, payload: ProductoUpdate) -> Producto:
    producto = _cargar_relaciones(uow, producto_id)
    cambios = payload.model_dump(exclude_unset=True)

    if "nombre" in cambios:
        producto.nombre = cambios["nombre"]
    if "descripcion" in cambios:
        producto.descripcion = cambios["descripcion"]
    if "precio_base" in cambios:
        producto.precio_base = cambios["precio_base"]
    if "margen_ganancia_porcentaje" in cambios:
        producto.margen_ganancia_porcentaje = cambios["margen_ganancia_porcentaje"]
    if "unidad_venta_id" in cambios:
        producto.unidad_venta_id = _validar_unidad_venta(uow, cambios["unidad_venta_id"])
    if "imagenes_url" in cambios:
        producto.imagenes_url = cambios["imagenes_url"]
    if "disponible" in cambios:
        producto.disponible = cambios["disponible"]
    if "categoria_ids" in cambios and cambios["categoria_ids"] is not None:
        producto.categorias = _expandir_hojas_con_padres(uow, cambios["categoria_ids"])
    if "ingredientes_configurados" in cambios or "ingrediente_ids" in cambios:
        configs = _validar_config_ingredientes(uow, _normalizar_config_ingredientes(payload))
        _aplicar_config_ingredientes(uow, producto_id, configs)

    producto.stock_cantidad = 0
    producto.updated_at = datetime.now(timezone.utc)

    try:
        producto = uow.productos.update(producto)
    except IntegrityError as exc:
        raise _integrity_error("No se pudo actualizar el producto.") from exc

    return _cargar_relaciones(uow, producto.id)


def cambiar_disponibilidad(uow: SQLModelUnitOfWork, producto_id: int, disponible: bool) -> Producto:
    producto = _cargar_relaciones(uow, producto_id)
    producto.disponible = disponible
    producto.updated_at = datetime.now(timezone.utc)
    try:
        producto = uow.productos.update(producto)
    except IntegrityError as exc:
        raise _integrity_error("No se pudo cambiar la disponibilidad del producto.") from exc
    return _cargar_relaciones(uow, producto.id)


def actualizar_stock(uow: SQLModelUnitOfWork, producto_id: int, stock_cantidad: int) -> Producto:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="El stock del producto se calcula automáticamente a partir del stock y consumo de sus ingredientes.",
    )


def eliminar(uow: SQLModelUnitOfWork, producto_id: int) -> None:
    producto = _cargar_relaciones(uow, producto_id)
    producto.activo = False
    producto.disponible = False
    producto.deleted_at = datetime.now(timezone.utc)
    producto.updated_at = producto.deleted_at
    try:
        uow.productos.update(producto)
    except IntegrityError as exc:
        raise _integrity_error("No se pudo eliminar el producto.") from exc


def activar(uow: SQLModelUnitOfWork, producto_id: int) -> Producto:
    producto = _cargar_relaciones(uow, producto_id, incluir_eliminados=True)
    producto.activo = True
    producto.deleted_at = None
    producto.disponible = True
    producto.updated_at = datetime.now(timezone.utc)
    try:
        producto = uow.productos.update(producto)
    except IntegrityError as exc:
        raise _integrity_error("No se pudo activar el producto.") from exc
    return _cargar_relaciones(uow, producto.id, incluir_eliminados=True)


def listar_ingredientes_producto(uow: SQLModelUnitOfWork, producto_id: int):
    producto = _cargar_relaciones(uow, producto_id)
    return getattr(producto, "ingredientes_configurados", [])


def asociar_ingrediente_producto(
    uow: SQLModelUnitOfWork,
    producto_id: int,
    payload: ProductoIngredientePayload,
):
    _cargar_relaciones(uow, producto_id)
    actuales = uow.productos.list_ingrediente_config(producto_id)
    configs: list[ProductoIngredientePayload] = []
    reemplazado = False

    for actual in actuales:
        if actual.ingrediente_id == payload.ingrediente_id:
            configs.append(payload)
            reemplazado = True
        else:
            configs.append(
                ProductoIngredientePayload(
                    ingrediente_id=actual.ingrediente_id,
                    cantidad=actual.cantidad,
                    unidad_medida_id=actual.unidad_medida_id,
                    es_removible=actual.es_removible,
                )
            )

    if not reemplazado:
        configs.append(payload)

    configs = _validar_config_ingredientes(uow, configs)
    _aplicar_config_ingredientes(uow, producto_id, configs)
    producto = _cargar_relaciones(uow, producto_id)
    for config in getattr(producto, "ingredientes_configurados", []):
        if config.ingrediente_id == payload.ingrediente_id:
            return config
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo asociar el ingrediente.")


def actualizar_imagenes(uow: SQLModelUnitOfWork, producto_id: int, imagenes_url: list[str]) -> Producto:
    producto = _cargar_relaciones(uow, producto_id)
    producto.imagenes_url = imagenes_url
    producto.updated_at = datetime.now(timezone.utc)
    try:
        producto = uow.productos.update(producto)
    except IntegrityError as exc:
        raise _integrity_error("No se pudieron actualizar las imágenes del producto.") from exc
    return _cargar_relaciones(uow, producto.id)
