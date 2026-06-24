from collections.abc import Generator
from types import TracebackType

from sqlmodel import Session

from app.core.db import engine
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.direccion_repository import DireccionRepository
from app.repositories.estado_pedido_repository import EstadoPedidoRepository
from app.repositories.forma_pago_repository import FormaPagoRepository
from app.repositories.ingrediente_repository import IngredienteRepository
from app.repositories.pedido_repository import PedidoRepository
from app.repositories.detalle_pedido_repository import DetallePedidoRepository
from app.repositories.historial_estado_repository import HistorialEstadoRepository
from app.repositories.producto_repository import ProductoRepository
from app.repositories.unidad_medida_repository import UnidadMedidaRepository
from app.repositories.rol_repository import RolRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.pago_repository import PagoRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.estadistica_repository import EstadisticaRepository
from app.repositories.configuracion_empresa_repository import ConfiguracionEmpresaRepository


class SQLModelUnitOfWork:
    session: Session
    categorias: CategoriaRepository
    ingredientes: IngredienteRepository
    productos: ProductoRepository
    roles: RolRepository
    usuarios: UsuarioRepository
    estados_pedido: EstadoPedidoRepository
    formas_pago: FormaPagoRepository
    direcciones: DireccionRepository
    pedidos: PedidoRepository
    detalles_pedido: DetallePedidoRepository
    historial_estados: HistorialEstadoRepository
    pagos: PagoRepository
    unidades_medida: UnidadMedidaRepository
    refresh_tokens: RefreshTokenRepository
    dashboard: DashboardRepository
    estadisticas: EstadisticaRepository
    configuracion_empresa: ConfiguracionEmpresaRepository

    def __enter__(self) -> "SQLModelUnitOfWork":
        try:
            self.session = Session(engine, expire_on_commit=False)
        except TypeError:
            # Compatibilidad con dobles de prueba que imitan Session sin kwargs.
            self.session = Session(engine)
        self.categorias = CategoriaRepository(self.session)
        self.ingredientes = IngredienteRepository(self.session)
        self.productos = ProductoRepository(self.session)
        self.roles = RolRepository(self.session)
        self.usuarios = UsuarioRepository(self.session)
        self.estados_pedido = EstadoPedidoRepository(self.session)
        self.formas_pago = FormaPagoRepository(self.session)
        self.direcciones = DireccionRepository(self.session)
        self.pedidos = PedidoRepository(self.session)
        self.detalles_pedido = DetallePedidoRepository(self.session)
        self.historial_estados = HistorialEstadoRepository(self.session)
        self.pagos = PagoRepository(self.session)
        self.unidades_medida = UnidadMedidaRepository(self.session)
        self.refresh_tokens = RefreshTokenRepository(self.session)
        self.dashboard = DashboardRepository(self.session)
        self.estadisticas = EstadisticaRepository(self.session)
        self.configuracion_empresa = ConfiguracionEmpresaRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            if exc_type is not None:
                self.session.rollback()
            else:
                self.session.commit()
        finally:
            self.session.close()


def get_uow() -> Generator[SQLModelUnitOfWork, None, None]:
    with SQLModelUnitOfWork() as uow:
        yield uow
