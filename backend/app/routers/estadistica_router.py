from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.auth_dependencies import UowDep, require_roles
from app.models.usuario import Usuario
from app.schemas.estadistica_schema import (
    EstadisticasResumenResponse,
    IngresosFormaPagoResponse,
    PedidosEstadoResponse,
    ProductosTopResponse,
    VentasPeriodoResponse,
)
from app.services import estadistica_service

router = APIRouter(prefix="/estadisticas", tags=["Estadísticas"])
AdminDep = Annotated[Usuario, Depends(require_roles("ADMIN"))]


@router.get("/resumen", response_model=EstadisticasResumenResponse)
def obtener_resumen_estadisticas(
    uow: UowDep,
    _admin: AdminDep,
    desde: Annotated[date | None, Query(description="Fecha inicial inclusive")] = None,
    hasta: Annotated[date | None, Query(description="Fecha final inclusive")] = None,
) -> EstadisticasResumenResponse:
    return estadistica_service.resumen(uow, desde=desde, hasta=hasta)


@router.get("/ventas", response_model=VentasPeriodoResponse)
def obtener_ventas_periodo(
    uow: UowDep,
    _admin: AdminDep,
    desde: Annotated[date | None, Query(description="Fecha inicial inclusive")] = None,
    hasta: Annotated[date | None, Query(description="Fecha final inclusive")] = None,
    agrupacion: Annotated[str, Query(pattern="^(day|week|month)$")] = "day",
) -> VentasPeriodoResponse:
    return estadistica_service.ventas_periodo(uow, desde=desde, hasta=hasta, agrupacion=agrupacion)


@router.get("/productos-top", response_model=ProductosTopResponse)
def obtener_productos_top(
    uow: UowDep,
    _admin: AdminDep,
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
) -> ProductosTopResponse:
    return estadistica_service.productos_top(uow, limit=limit)


@router.get("/pedidos-por-estado", response_model=PedidosEstadoResponse)
def obtener_pedidos_por_estado(
    uow: UowDep,
    _admin: AdminDep,
) -> PedidosEstadoResponse:
    return estadistica_service.pedidos_por_estado(uow)


@router.get("/ingresos", response_model=IngresosFormaPagoResponse)
def obtener_ingresos_por_forma_pago(
    uow: UowDep,
    _admin: AdminDep,
    desde: Annotated[date | None, Query(description="Fecha inicial inclusive")] = None,
    hasta: Annotated[date | None, Query(description="Fecha final inclusive")] = None,
) -> IngresosFormaPagoResponse:
    return estadistica_service.ingresos_por_forma_pago(uow, desde=desde, hasta=hasta)
