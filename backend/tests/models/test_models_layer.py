from decimal import Decimal

from app.models.categoria import Categoria
from app.models.detalle_pedido import DetallePedido
from app.models.pedido import Pedido
from app.models.producto import Producto
from app.models.producto_ingrediente import ProductoIngrediente
from app.models.refresh_token import RefreshToken
from app.models.unidad_medida import UnidadMedida
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol


def test_usuario_defaults_active_and_soft_delete_empty(now_utc):
    usuario = Usuario(email="u@test.com", nombre="Lucas", password_hash="hash")
    assert usuario.activo is True
    assert usuario.deleted_at is None
    assert usuario.email == "u@test.com"


def test_categoria_defaults_support_hierarchy_and_image():
    categoria = Categoria(nombre="Bebidas", parent_id=None, imagen_url="https://img.test/a.png")
    assert categoria.parent_id is None
    assert categoria.imagen_url.endswith(".png")
    assert categoria.activo is True


def test_producto_defaults_match_catalog_requirements():
    producto = Producto(nombre="Limonada", precio_base=Decimal("1200.00"))
    assert producto.imagenes_url == []
    assert producto.disponible is True
    assert producto.stock_cantidad == 0
    assert producto.deleted_at is None


def test_producto_imagenes_url_default_is_not_shared_between_instances():
    producto_a = Producto(nombre="A")
    producto_b = Producto(nombre="B")
    producto_a.imagenes_url.append("https://img.test/a.png")
    assert producto_b.imagenes_url == []


def test_pedido_defaults_start_as_pendiente():
    pedido = Pedido(usuario_id=1, forma_pago_codigo="EFECTIVO")
    assert pedido.estado_codigo == "PENDIENTE"
    assert pedido.subtotal == Decimal("0")
    assert pedido.activo is True


def test_detalle_pedido_uses_snapshot_fields():
    detalle = DetallePedido(
        pedido_id=1,
        producto_id=2,
        cantidad=3,
        nombre_producto_snap="Pizza",
        precio_unitario_snap=Decimal("1000.00"),
        subtotal_snap=Decimal("3000.00"),
    )
    assert detalle.nombre_producto_snap == "Pizza"
    assert detalle.subtotal_snap == Decimal("3000.00")


def test_producto_ingrediente_has_quantity_unit_and_removable_flag():
    receta = ProductoIngrediente(producto_id=1, ingrediente_id=2, cantidad=Decimal("1.500"), unidad_medida_id=3)
    assert receta.cantidad == Decimal("1.500")
    assert receta.unidad_medida_id == 3
    assert receta.es_removible is True


def test_refresh_token_and_usuario_rol_optional_fields(now_utc):
    refresh = RefreshToken(usuario_id=1, token_hash="abc", expires_at=now_utc)
    usuario_rol = UsuarioRol(usuario_id=1, rol_id=2)
    unidad = UnidadMedida(nombre="Kilogramo", simbolo="kg", tipo="peso")
    assert refresh.revoked_at is None
    assert usuario_rol.expires_at is None
    assert unidad.activo is True
