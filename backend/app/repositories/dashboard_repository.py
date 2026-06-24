from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.detalle_pedido import DetallePedido
from app.models.ingrediente import Ingrediente
from app.models.pago import Pago
from app.models.pedido import Pedido
from app.models.producto import Producto
from app.models.unidad_medida import UnidadMedida
from app.models.usuario import Usuario


class DashboardRepository:
    """Consultas agregadas del dashboard administrativo.

    Mantiene los SELECT y agregaciones dentro de la capa repository para que
    los services solo orquesten reglas de negocio y mapeen respuestas.
    """

    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _fecha_desde_db(value: Any) -> date:
        if isinstance(value, date):
            return value
        return datetime.strptime(str(value), "%Y-%m-%d").date()

    def _scalar_int(self, statement) -> int:
        value = self.session.exec(statement).one()
        return int(value or 0)

    def _scalar_decimal(self, statement) -> Decimal:
        value = self.session.exec(statement).one()
        return Decimal(str(value or 0))

    def obtener_metricas_generales(self, estados_venta: list[str], inicio_hoy: datetime) -> dict[str, Any]:
        productos_activos = self._scalar_int(
            select(func.count(Producto.id)).where(
                Producto.activo == True,  # noqa: E712
                Producto.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        ingredientes_activos = self._scalar_int(
            select(func.count(Ingrediente.id)).where(
                Ingrediente.activo == True,  # noqa: E712
                Ingrediente.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        usuarios_activos = self._scalar_int(
            select(func.count(Usuario.id)).where(
                Usuario.activo == True,  # noqa: E712
                Usuario.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        pedidos_activos = self._scalar_int(
            select(func.count(Pedido.id)).where(
                Pedido.activo == True,  # noqa: E712
                Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        pedidos_hoy = self._scalar_int(
            select(func.count(Pedido.id)).where(
                Pedido.created_at >= inicio_hoy,
                Pedido.activo == True,  # noqa: E712
                Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        pagos_aprobados = self._scalar_int(
            select(func.count(Pago.id)).where(
                Pago.estado == "aprobado",
                Pago.activo == True,  # noqa: E712
                Pago.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        pagos_rechazados = self._scalar_int(
            select(func.count(Pago.id)).where(
                Pago.estado.in_(["rechazado", "rejected"]),
                Pago.activo == True,  # noqa: E712
                Pago.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        stock_critico = self._scalar_int(
            select(func.count(Ingrediente.id)).where(
                Ingrediente.stock_cantidad <= 5,
                Ingrediente.activo == True,  # noqa: E712
                Ingrediente.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        ventas_confirmadas = self._scalar_decimal(
            select(func.coalesce(func.sum(Pedido.total), 0)).where(
                Pedido.estado_codigo.in_(estados_venta),
                Pedido.activo == True,  # noqa: E712
                Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        ventas_hoy = self._scalar_decimal(
            select(func.coalesce(func.sum(Pedido.total), 0)).where(
                Pedido.created_at >= inicio_hoy,
                Pedido.estado_codigo.in_(estados_venta),
                Pedido.activo == True,  # noqa: E712
                Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        pedidos_venta = self._scalar_int(
            select(func.count(Pedido.id)).where(
                Pedido.estado_codigo.in_(estados_venta),
                Pedido.activo == True,  # noqa: E712
                Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
            )
        )
        return {
            "productos_activos": productos_activos,
            "ingredientes_activos": ingredientes_activos,
            "usuarios_activos": usuarios_activos,
            "pedidos_activos": pedidos_activos,
            "pedidos_hoy": pedidos_hoy,
            "pagos_aprobados": pagos_aprobados,
            "pagos_rechazados": pagos_rechazados,
            "stock_critico": stock_critico,
            "ventas_confirmadas": ventas_confirmadas,
            "ventas_hoy": ventas_hoy,
            "pedidos_venta": pedidos_venta,
        }

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

    def obtener_ventas_por_forma_pago(self, estados_venta: list[str]) -> list[tuple[Any, Any, Any]]:
        return list(
            self.session.exec(
                select(
                    Pedido.forma_pago_codigo,
                    func.count(Pedido.id),
                    func.coalesce(func.sum(Pedido.total), 0),
                )
                .where(
                    Pedido.estado_codigo.in_(estados_venta),
                    Pedido.activo == True,  # noqa: E712
                    Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
                )
                .group_by(Pedido.forma_pago_codigo)
                .order_by(func.coalesce(func.sum(Pedido.total), 0).desc())
            ).all()
        )

    def obtener_pedidos_ultimos_7_dias(self, estados_venta: list[str], inicio_7_dias: datetime) -> list[tuple[Any, Any, Any]]:
        return list(
            self.session.exec(
                select(
                    func.date(Pedido.created_at),
                    func.count(Pedido.id),
                    func.coalesce(func.sum(Pedido.total), 0),
                )
                .where(
                    Pedido.created_at >= inicio_7_dias,
                    Pedido.estado_codigo.in_(estados_venta),
                    Pedido.activo == True,  # noqa: E712
                    Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
                )
                .group_by(func.date(Pedido.created_at))
                .order_by(func.date(Pedido.created_at))
            ).all()
        )

    def obtener_top_productos(self, estados_venta: list[str], limit: int = 5) -> list[tuple[Any, Any, Any, Any]]:
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
                    Pedido.estado_codigo.in_(estados_venta),
                    Pedido.activo == True,  # noqa: E712
                    Pedido.deleted_at.is_(None),  # type: ignore[attr-defined]
                )
                .group_by(DetallePedido.producto_id, DetallePedido.nombre_producto_snap)
                .order_by(func.coalesce(func.sum(DetallePedido.cantidad), 0).desc())
                .limit(limit)
            ).all()
        )

    def obtener_ingredientes_stock_bajo(self, limit: int = 6) -> list[tuple[Any, Any, Any, Any]]:
        return list(
            self.session.exec(
                select(Ingrediente.id, Ingrediente.nombre, Ingrediente.stock_cantidad, UnidadMedida.simbolo)
                .join(UnidadMedida, UnidadMedida.id == Ingrediente.unidad_medida_id, isouter=True)
                .where(
                    Ingrediente.stock_cantidad <= 5,
                    Ingrediente.activo == True,  # noqa: E712
                    Ingrediente.deleted_at.is_(None),  # type: ignore[attr-defined]
                )
                .order_by(Ingrediente.stock_cantidad.asc(), Ingrediente.nombre.asc())
                .limit(limit)
            ).all()
        )
