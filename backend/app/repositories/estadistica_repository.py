from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.detalle_pedido import DetallePedido
from app.models.ingrediente import Ingrediente
from app.models.pedido import Pedido
from app.models.producto import Producto

ESTADOS_COMERCIALES = {"CONFIRMADO", "EN_PREP", "ENTREGADO"}


class EstadisticaRepository:
    """Consultas de estadísticas del sistema.

    Centraliza SELECT, JOIN, GROUP BY y SUM para que los services no consulten
    la base directamente.
    """

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def datetime_start(day: date) -> datetime:
        return datetime.combine(day, datetime.min.time(), tzinfo=timezone.utc)

    @classmethod
    def datetime_end_exclusive(cls, day: date) -> datetime:
        return cls.datetime_start(day + timedelta(days=1))

    @staticmethod
    def to_decimal(value: Any) -> Decimal:
        return Decimal(str(value or 0)).quantize(Decimal("0.01"))

    @staticmethod
    def to_date(value: Any) -> date:
        if isinstance(value, date):
            return value
        return datetime.strptime(str(value), "%Y-%m-%d").date()

    def obtener_resumen(self, desde: date, hasta: date, hoy: date) -> dict[str, Any]:
        ventas_periodo = self.session.exec(
            select(func.coalesce(func.sum(Pedido.total), 0)).where(
                Pedido.estado_codigo.in_(ESTADOS_COMERCIALES),
                Pedido.created_at >= self.datetime_start(desde),
                Pedido.created_at < self.datetime_end_exclusive(hasta),
                Pedido.activo == True,  # noqa: E712
                Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        ).one()
        ventas_hoy = self.session.exec(
            select(func.coalesce(func.sum(Pedido.total), 0)).where(
                Pedido.estado_codigo.in_(ESTADOS_COMERCIALES),
                Pedido.created_at >= self.datetime_start(hoy),
                Pedido.activo == True,  # noqa: E712
                Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        ).one()
        pedidos_confirmados = self.session.exec(
            select(func.count(Pedido.id)).where(
                Pedido.estado_codigo.in_(ESTADOS_COMERCIALES),
                Pedido.created_at >= self.datetime_start(desde),
                Pedido.created_at < self.datetime_end_exclusive(hasta),
                Pedido.activo == True,  # noqa: E712
                Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        ).one()
        pedidos_activos = self.session.exec(
            select(func.count(Pedido.id)).where(
                Pedido.estado_codigo.notin_({"CANCELADO", "ENTREGADO"}),
                Pedido.activo == True,  # noqa: E712
                Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        ).one()
        productos_activos = self.session.exec(
            select(func.count(Producto.id)).where(
                Producto.activo == True,  # noqa: E712
                Producto.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        ).one()
        stock_critico = self.session.exec(
            select(func.count(Ingrediente.id)).where(
                Ingrediente.stock_cantidad <= 5,
                Ingrediente.activo == True,  # noqa: E712
                Ingrediente.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        ).one()
        return {
            "ventas_periodo": self.to_decimal(ventas_periodo),
            "ventas_hoy": self.to_decimal(ventas_hoy),
            "pedidos_confirmados": int(pedidos_confirmados or 0),
            "pedidos_activos": int(pedidos_activos or 0),
            "productos_activos": int(productos_activos or 0),
            "stock_critico": int(stock_critico or 0),
        }

    def obtener_ventas_periodo(self, desde: date, hasta: date) -> list[tuple[Any, Any, Any]]:
        return list(
            self.session.exec(
                select(func.date(Pedido.created_at), func.coalesce(func.sum(Pedido.total), 0), func.count(Pedido.id))
                .where(
                    Pedido.estado_codigo.in_(ESTADOS_COMERCIALES),
                    Pedido.created_at >= self.datetime_start(desde),
                    Pedido.created_at < self.datetime_end_exclusive(hasta),
                    Pedido.activo == True,  # noqa: E712
                    Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
                )
                .group_by(func.date(Pedido.created_at))
                .order_by(func.date(Pedido.created_at))
            ).all()
        )

    def obtener_productos_top(self, limit: int = 5) -> list[tuple[Any, Any, Any, Any]]:
        return list(
            self.session.exec(
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
        )

    def obtener_pedidos_por_estado(self) -> list[tuple[Any, Any]]:
        return list(
            self.session.exec(
                select(Pedido.estado_codigo, func.count(Pedido.id))
                .where(
                    Pedido.activo == True,  # noqa: E712
                    Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
                )
                .group_by(Pedido.estado_codigo)
                .order_by(Pedido.estado_codigo)
            ).all()
        )

    def obtener_ingresos_por_forma_pago(self, desde: date, hasta: date) -> list[tuple[Any, Any, Any]]:
        return list(
            self.session.exec(
                select(Pedido.forma_pago_codigo, func.coalesce(func.sum(Pedido.total), 0), func.count(Pedido.id))
                .where(
                    Pedido.estado_codigo.in_(ESTADOS_COMERCIALES),
                    Pedido.created_at >= self.datetime_start(desde),
                    Pedido.created_at < self.datetime_end_exclusive(hasta),
                    Pedido.activo == True,  # noqa: E712
                    Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
                )
                .group_by(Pedido.forma_pago_codigo)
                .order_by(func.coalesce(func.sum(Pedido.total), 0).desc())
            ).all()
        )
