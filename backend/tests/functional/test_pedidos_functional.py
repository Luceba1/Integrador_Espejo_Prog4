from decimal import Decimal
from types import SimpleNamespace

from app.models.estado_pedido import EstadoPedido
from app.models.historial_estado_pedido import HistorialEstadoPedido
from app.models.pedido import Pedido
from app.services import pedido_service
from tests.conftest import DummyRepo


class PedidoRepo(DummyRepo):
    def get_active_with_details(self, entity_id: int):
        return self.get_active_by_id(entity_id)


class FlushSession:
    def flush(self):
        return None


def test_pedidos_functional_uses_official_en_prep_state(admin_user, now_utc):
    pedido = Pedido(
        id=10,
        usuario_id=admin_user.id,
        estado_codigo="CONFIRMADO",
        forma_pago_codigo="EFECTIVO",
        subtotal=Decimal("100.00"),
        descuento=Decimal("0.00"),
        costo_envio=Decimal("0.00"),
        total=Decimal("100.00"),
        created_at=now_utc,
        updated_at=now_utc,
    )
    pedido.historial_estados = [
        HistorialEstadoPedido(id=1, pedido_id=10, estado_desde=None, estado_hacia="PENDIENTE", created_at=now_utc)
    ]

    uow = SimpleNamespace(
        pedidos=PedidoRepo([pedido]),
        estados_pedido=DummyRepo(
            [
                EstadoPedido(codigo="CONFIRMADO", nombre="Confirmado", orden=2, activo=True, es_final=False),
                EstadoPedido(codigo="EN_PREP", nombre="En preparación", orden=3, activo=True, es_final=False),
            ]
        ),
        historial_estados=DummyRepo(),
        session=FlushSession(),
    )

    actualizado = pedido_service.avanzar_estado(
        uow,
        pedido_id=10,
        nuevo_estado_codigo="EN_PREP",
        usuario=admin_user,
        motivo="Pasa a cocina.",
    )

    assert pedido_service.ESTADO_EN_PREP == "EN_PREP"
    assert actualizado.estado_codigo == "EN_PREP"
    assert uow.historial_estados.created[-1].estado_desde == "CONFIRMADO"
    assert uow.historial_estados.created[-1].estado_hacia == "EN_PREP"
