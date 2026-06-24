from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from app.repositories.estadistica_repository import ESTADOS_COMERCIALES
from app.schemas.estadistica_schema import (
    EstadisticasResumenResponse,
    IngresosFormaPagoItem,
    IngresosFormaPagoResponse,
    PedidosEstadoItem,
    PedidosEstadoResponse,
    ProductoTopItem,
    ProductosTopResponse,
    VentasPeriodoItem,
    VentasPeriodoResponse,
)
from app.uow.unit_of_work import SQLModelUnitOfWork


def _range_defaults(desde: date | None, hasta: date | None) -> tuple[date, date]:
    hoy = datetime.now(timezone.utc).date()
    return desde or (hoy - timedelta(days=6)), hasta or hoy


def resumen(uow: SQLModelUnitOfWork, desde: date | None = None, hasta: date | None = None) -> EstadisticasResumenResponse:
    desde, hasta = _range_defaults(desde, hasta)
    hoy = datetime.now(timezone.utc).date()
    datos = uow.estadisticas.obtener_resumen(desde=desde, hasta=hasta, hoy=hoy)

    pedidos_confirmados = datos["pedidos_confirmados"]
    ventas_periodo = datos["ventas_periodo"]
    ticket = (ventas_periodo / pedidos_confirmados).quantize(Decimal("0.01")) if pedidos_confirmados else Decimal("0.00")

    return EstadisticasResumenResponse(
        ventas_hoy=datos["ventas_hoy"],
        ventas_periodo=ventas_periodo,
        ticket_promedio=ticket,
        pedidos_activos=datos["pedidos_activos"],
        pedidos_confirmados=pedidos_confirmados,
        productos_activos=datos["productos_activos"],
        stock_critico=datos["stock_critico"],
    )


def ventas_periodo(
    uow: SQLModelUnitOfWork,
    desde: date | None = None,
    hasta: date | None = None,
    agrupacion: str = "day",
) -> VentasPeriodoResponse:
    desde, hasta = _range_defaults(desde, hasta)
    agrupacion = agrupacion.lower().strip()
    if agrupacion not in {"day", "week", "month"}:
        agrupacion = "day"

    filas = uow.estadisticas.obtener_ventas_periodo(desde=desde, hasta=hasta)
    items = [
        VentasPeriodoItem(
            periodo=uow.estadisticas.to_date(periodo),
            label=uow.estadisticas.to_date(periodo).strftime("%d/%m"),
            total_ventas=uow.estadisticas.to_decimal(total),
            cantidad_pedidos=int(cantidad or 0),
        )
        for periodo, total, cantidad in filas
    ]
    return VentasPeriodoResponse(desde=desde, hasta=hasta, agrupacion=agrupacion, items=items)


def productos_top(uow: SQLModelUnitOfWork, limit: int = 5) -> ProductosTopResponse:
    filas = uow.estadisticas.obtener_productos_top(limit=limit)
    return ProductosTopResponse(
        items=[
            ProductoTopItem(
                producto_id=int(producto_id),
                nombre=str(nombre),
                cantidad_vendida=int(cantidad or 0),
                ingresos=uow.estadisticas.to_decimal(ingresos),
            )
            for producto_id, nombre, cantidad, ingresos in filas
        ]
    )


def pedidos_por_estado(uow: SQLModelUnitOfWork) -> PedidosEstadoResponse:
    filas = uow.estadisticas.obtener_pedidos_por_estado()
    return PedidosEstadoResponse(
        items=[PedidosEstadoItem(estado_codigo=str(estado), cantidad=int(cantidad or 0)) for estado, cantidad in filas]
    )


def ingresos_por_forma_pago(
    uow: SQLModelUnitOfWork,
    desde: date | None = None,
    hasta: date | None = None,
) -> IngresosFormaPagoResponse:
    desde, hasta = _range_defaults(desde, hasta)
    filas = uow.estadisticas.obtener_ingresos_por_forma_pago(desde=desde, hasta=hasta)
    return IngresosFormaPagoResponse(
        desde=desde,
        hasta=hasta,
        items=[
            IngresosFormaPagoItem(
                forma_pago_codigo=str(forma_pago),
                total=uow.estadisticas.to_decimal(total),
                cantidad_pedidos=int(cantidad or 0),
            )
            for forma_pago, total, cantidad in filas
        ],
    )
