from types import SimpleNamespace

from app.core.security import verify_password
from app.models.rol import Rol
from app.schemas.auth_schema import UsuarioRegister
from app.services import auth_service
from tests.conftest import DummyRepo


def test_auth_functional_registers_client_with_hashed_password_and_role():
    rol_cliente = Rol(id=4, codigo="CLIENT", nombre="Cliente", activo=True)
    usuarios_repo = DummyRepo()
    uow = SimpleNamespace(usuarios=usuarios_repo, roles=DummyRepo([rol_cliente]))

    usuario = auth_service.registrar_cliente(
        uow,
        UsuarioRegister(
            email=" CLIENTE@TEST.COM ",
            nombre="Cliente",
            apellido="Demo",
            password="Password123",
        ),
    )

    assert usuario.email == "cliente@test.com"
    assert usuario.roles[0].codigo == "CLIENT"
    assert usuario.password_hash != "Password123"
    assert verify_password("Password123", usuario.password_hash)
    assert usuarios_repo.created[-1] is usuario
