from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.auth_schema import LoginRequest, UsuarioRegister
from app.schemas.categoria_schema import CategoriaCreate, CategoriaTreeRead
from app.schemas.direccion_schema import DireccionCreate
from app.schemas.pedido_schema import PedidoCreate, PedidoEstadoUpdate, PedidoItemCreate
from app.schemas.producto_schema import ProductoCreate, ProductoIngredientePayload
from app.schemas.unidad_medida_schema import UnidadMedidaCreate, UnidadMedidaUpdate


def test_usuario_register_validates_email_and_minimum_password():
    payload = UsuarioRegister(email="lucas@test.com", nombre="Lucas", apellido="Pujada", password="Password123")
    assert payload.email == "lucas@test.com"
    assert payload.nombre == "Lucas"


def test_usuario_register_rejects_invalid_email():
    with pytest.raises(ValidationError):
        UsuarioRegister(email="no-es-email", nombre="Lucas", password="Password123")


def test_login_request_accepts_email_and_password():
    payload = LoginRequest(email="admin@test.com", password="Admin1234")
    assert payload.password == "Admin1234"


def test_pedido_create_requires_at_least_one_item():
    with pytest.raises(ValidationError):
        PedidoCreate(forma_pago_codigo="EFECTIVO", items=[])


def test_pedido_item_and_cancelacion_schema_support_personalizacion_and_stock_flag():
    item = PedidoItemCreate(producto_id=1, cantidad=2, personalizacion={"removidos": [3]})
    estado = PedidoEstadoUpdate(estado_codigo="CANCELADO", motivo="Sin stock", recuperar_stock=False)
    assert item.personalizacion == {"removidos": [3]}
    assert estado.recuperar_stock is False


def test_producto_ingrediente_rejects_zero_quantity():
    with pytest.raises(ValidationError):
        ProductoIngredientePayload(ingrediente_id=1, cantidad=Decimal("0"))


def test_producto_create_default_lists_are_empty():
    producto = ProductoCreate(nombre="Pizza", precio_base=Decimal("1000.00"))
    assert producto.categoria_ids == []
    assert producto.ingredientes_configurados == []


def test_direccion_create_validates_latitud_and_longitud_ranges():
    DireccionCreate(linea1="Calle 123", ciudad="Mendoza", latitud=Decimal("-32.88"), longitud=Decimal("-68.83"))
    with pytest.raises(ValidationError):
        DireccionCreate(linea1="Calle 123", ciudad="Mendoza", latitud=Decimal("100"))


def test_categoria_tree_read_has_children_default_list(now_utc):
    categoria = CategoriaTreeRead(id=1, nombre="Bebidas", activo=True, created_at=now_utc, updated_at=now_utc)
    assert categoria.hijos == []


def test_unidad_medida_create_and_update_validate_lengths():
    unidad = UnidadMedidaCreate(nombre="Kilogramo", simbolo="kg", tipo="peso")
    update = UnidadMedidaUpdate(simbolo="g")
    assert unidad.activo is True
    assert update.simbolo == "g"
