from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func
from sqlmodel import select

from app.models.detalle_pedido import DetallePedido
from app.models.ingrediente import Ingrediente
from app.models.pedido import Pedido
from app.models.producto import Producto
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

# TPI v6 / EST-01: no incluir CANCELADO en métricas comerciales.
# Se consideran ventas confirmadas los pedidos que ya pasaron el pago o la confirmación manual.
ESTADOS_COMERCIALES = {"CONFIRMADO", "EN_PREPARACION", "EN_PREP", "ENTREGADO"}


def _to_decimal(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal("0.01"))


def _to_date(value) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def _range_defaults(desde: date | None, hasta: date | None) -> tuple[date, date]:
    hoy = datetime.now(timezone.utc).date()
    return desde or (hoy - timedelta(days=6)), hasta or hoy


def _datetime_start(day: date) -> datetime:
    return datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)


def _datetime_end_exclusive(day: date) -> datetime:
    return _datetime_start(day + timedelta(days=1))


def _base_pedidos_comerciales(desde: date | None = None, hasta: date | None = None):
    statement = select(Pedido).where(
        Pedido.estado_codigo.in_(ESTADOS_COMERCIALES),
        Pedido.activo == True,  # noqa: E712
        Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
    )
    if desde is not None:
        statement = statement.where(Pedido.created_at >= _datetime_start(desde))
    if hasta is not None:
        statement = statement.where(Pedido.created_at < _datetime_end_exclusive(hasta))
    return statement


def resumen(uow: SQLModelUnitOfWork, desde: date | None = None, hasta: date | None = None) -> EstadisticasResumenResponse:
    desde, hasta = _range_defaults(desde, hasta)
    hoy = datetime.now(timezone.utc).date()

    ventas_periodo = _to_decimal(
        uow.session.exec(
            select(func.coalesce(func.sum(Pedido.total), 0)).where(
                Pedido.estado_codigo.in_(ESTADOS_COMERCIALES),
                Pedido.created_at >= _datetime_start(desde),
                Pedido.created_at < _datetime_end_exclusive(hasta),
                Pedido.activo == True,  # noqa: E712
                Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        ).one()
    )
    ventas_hoy = _to_decimal(
        uow.session.exec(
            select(func.coalesce(func.sum(Pedido.total), 0)).where(
                Pedido.estado_codigo.in_(ESTADOS_COMERCIALES),
                Pedido.created_at >= _datetime_start(hoy),
                Pedido.activo == True,  # noqa: E712
                Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        ).one()
    )
    pedidos_confirmados = int(
        uow.session.exec(
            select(func.count(Pedido.id)).where(
                Pedido.estado_codigo.in_(ESTADOS_COMERCIALES),
                Pedido.created_at >= _datetime_start(desde),
                Pedido.created_at < _datetime_end_exclusive(hasta),
                Pedido.activo == True,  # noqa: E712
                Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        ).one()
        or 0
    )
    pedidos_activos = int(
        uow.session.exec(
            select(func.count(Pedido.id)).where(
                Pedido.estado_codigo.notin_({"CANCELADO", "ENTREGADO"}),
                Pedido.activo == True,  # noqa: E712
                Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        ).one()
        or 0
    )
    productos_activos = int(
        uow.session.exec(
            select(func.count(Producto.id)).where(
                Producto.activo == True,  # noqa: E712
                Producto.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        ).one()
        or 0
    )
    stock_critico = int(
        uow.session.exec(
            select(func.count(Ingrediente.id)).where(
                Ingrediente.stock_cantidad <= 5,
                Ingrediente.activo == True,  # noqa: E712
                Ingrediente.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        ).one()
        or 0
    )

    ticket = (ventas_periodo / pedidos_confirmados).quantize(Decimal("0.01")) if pedidos_confirmados else Decimal("0.00")
    return EstadisticasResumenResponse(
        ventas_hoy=ventas_hoy,
        ventas_periodo=ventas_periodo,
        ticket_promedio=ticket,
        pedidos_activos=pedidos_activos,
        pedidos_confirmados=pedidos_confirmados,
        productos_activos=productos_activos,
        stock_critico=stock_critico,
    )


def ventas_periodo(uow: SQLModelUnitOfWork, desde: date | None = None, hasta: date | None = None, agrupacion: str = "day") -> VentasPeriodoResponse:
    desde, hasta = _range_defaults(desde, hasta)
    agrupacion = agrupacion.lower().strip()
    if agrupacion not in {"day", "week", "month"}:
        agrupacion = "day"

    # Implementación portable para SQLite/PostgreSQL en demo local/tests. En PostgreSQL
    # se puede reemplazar por DATE_TRUNC si se desea granularidad semanal/mensual real.
    filas = uow.session.exec(
        select(func.date(Pedido.created_at), func.coalesce(func.sum(Pedido.total), 0), func.count(Pedido.id))
        .where(
            Pedido.estado_codigo.in_(ESTADOS_COMERCIALES),
            Pedido.created_at >= _datetime_start(desde),
            Pedido.created_at < _datetime_end_exclusive(hasta),
            Pedido.activo == True,  # noqa: E712
            Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
        )
        .group_by(func.date(Pedido.created_at))
        .order_by(func.date(Pedido.created_at))
    ).all()

    items = [
        VentasPeriodoItem(
            periodo=_to_date(periodo),
            label=_to_date(periodo).strftime("%d/%m"),
            total_ventas=_to_decimal(total),
            cantidad_pedidos=int(cantidad or 0),
        )
        for periodo, total, cantidad in filas
    ]
    return VentasPeriodoResponse(desde=desde, hasta=hasta, agrupacion=agrupacion, items=items)


def productos_top(uow: SQLModelUnitOfWork, limit: int = 5) -> ProductosTopResponse:
    filas = uow.session.exec(
        select(
            DetallePedido.producto_id,
            DetallePedido.nombre_producto_snap,
            func.coalesce(func.sum(DetallePedido.cantidad), 0),
            func.coalesce(func.sum(DetallePedido.subtotal_snap), 0),
        )
        .join(Pedido, Pedido.id == DetallePedido.pedido_id)
        .where(
            Pedido.estado_codigo.in_(ESTADOS_COMERCIALES),
            Pedido.activo == True,  # noqa: E712
            Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
        )
        .group_by(DetallePedido.producto_id, DetallePedido.nombre_producto_snap)
        .order_by(func.coalesce(func.sum(DetallePedido.subtotal_snap), 0).desc())
        .limit(limit)
    ).all()

    return ProductosTopResponse(
        items=[
            ProductoTopItem(
                producto_id=int(producto_id),
                nombre=str(nombre),
                cantidad_vendida=int(cantidad or 0),
                ingresos=_to_decimal(ingresos),
            )
            for producto_id, nombre, cantidad, ingresos in filas
        ]
    )


def pedidos_por_estado(uow: SQLModelUnitOfWork) -> PedidosEstadoResponse:
    filas = uow.session.exec(
        select(Pedido.estado_codigo, func.count(Pedido.id))
        .where(
            Pedido.activo == True,  # noqa: E712
            Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
        )
        .group_by(Pedido.estado_codigo)
        .order_by(Pedido.estado_codigo)
    ).all()

    return PedidosEstadoResponse(
        items=[PedidosEstadoItem(estado_codigo=str(estado), cantidad=int(cantidad or 0)) for estado, cantidad in filas]
    )


def ingresos_por_forma_pago(uow: SQLModelUnitOfWork, desde: date | None = None, hasta: date | None = None) -> IngresosFormaPagoResponse:
    desde, hasta = _range_defaults(desde, hasta)
    filas = uow.session.exec(
        select(Pedido.forma_pago_codigo, func.coalesce(func.sum(Pedido.total), 0), func.count(Pedido.id))
        .where(
            Pedido.estado_codigo.in_(ESTADOS_COMERCIALES),
            Pedido.created_at >= _datetime_start(desde),
            Pedido.created_at < _datetime_end_exclusive(hasta),
            Pedido.activo == True,  # noqa: E712
            Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
        )
        .group_by(Pedido.forma_pago_codigo)
        .order_by(func.coalesce(func.sum(Pedido.total), 0).desc())
    ).all()

    return IngresosFormaPagoResponse(
        desde=desde,
        hasta=hasta,
        items=[
            IngresosFormaPagoItem(
                forma_pago_codigo=str(forma_pago),
                total=_to_decimal(total),
                cantidad_pedidos=int(cantidad or 0),
            )
            for forma_pago, total, cantidad in filas
        ],
    )
