from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.auth_dependencies import get_current_user
from app.routers import auth_router, categoria_router, unidad_medida_router
from app.uow.unit_of_work import get_uow
from app.models.categoria import Categoria
from app.models.rol import Rol
from app.models.unidad_medida import UnidadMedida
from app.models.usuario import Usuario


class DummyUOW(SimpleNamespace):
    pass


def _test_app(admin_user):
    app = FastAPI()
    app.include_router(auth_router.router, prefix="/api/v1")
    app.include_router(categoria_router.router, prefix="/api/v1")
    app.include_router(unidad_medida_router.router, prefix="/api/v1")
    app.dependency_overrides[get_uow] = lambda: DummyUOW()
    app.dependency_overrides[get_current_user] = lambda: admin_user
    return app


def test_health_like_router_can_list_categorias_public(monkeypatch, admin_user, now_utc):
    categoria = Categoria(id=1, nombre="Bebidas", activo=True, created_at=now_utc, updated_at=now_utc)
    monkeypatch.setattr(categoria_router.categoria_service, "listar", lambda *args, **kwargs: [categoria])
    client = TestClient(_test_app(admin_user))
    response = client.get("/api/v1/categorias/")
    assert response.status_code == 200
    assert response.json()[0]["nombre"] == "Bebidas"


def test_categoria_post_returns_201_for_admin(monkeypatch, admin_user, now_utc):
    categoria = Categoria(id=1, nombre="Comidas", activo=True, created_at=now_utc, updated_at=now_utc)
    monkeypatch.setattr(categoria_router.categoria_service, "crear", lambda *args, **kwargs: categoria)
    client = TestClient(_test_app(admin_user))
    response = client.post("/api/v1/categorias/", json={"nombre": "Comidas"})
    assert response.status_code == 201
    assert response.json()["nombre"] == "Comidas"


def test_categoria_delete_returns_204(monkeypatch, admin_user):
    called = {}

    def fake_eliminar(uow, categoria_id):
        called["categoria_id"] = categoria_id

    monkeypatch.setattr(categoria_router.categoria_service, "eliminar", fake_eliminar)
    client = TestClient(_test_app(admin_user))
    response = client.delete("/api/v1/categorias/3")
    assert response.status_code == 204
    assert called["categoria_id"] == 3


def test_unidad_medida_get_list_returns_units(monkeypatch, admin_user, now_utc):
    unidad = UnidadMedida(id=1, nombre="Unidad", simbolo="u", tipo="contable", activo=True, created_at=now_utc, updated_at=now_utc)
    monkeypatch.setattr(unidad_medida_router.unidad_medida_service, "listar", lambda *args, **kwargs: [unidad])
    client = TestClient(_test_app(admin_user))
    response = client.get("/api/v1/unidades-medida/")
    assert response.status_code == 200
    assert response.json()[0]["simbolo"] == "u"


def test_unidad_medida_post_validates_body_and_returns_201(monkeypatch, admin_user, now_utc):
    unidad = UnidadMedida(id=1, nombre="Kilogramo", simbolo="kg", tipo="peso", activo=True, created_at=now_utc, updated_at=now_utc)
    monkeypatch.setattr(unidad_medida_router.unidad_medida_service, "crear", lambda *args, **kwargs: unidad)
    client = TestClient(_test_app(admin_user))
    response = client.post("/api/v1/unidades-medida/", json={"nombre": "Kilogramo", "simbolo": "kg", "tipo": "peso"})
    assert response.status_code == 201
    assert response.json()["simbolo"] == "kg"


def test_auth_login_sets_access_and_refresh_cookies(monkeypatch, now_utc):
    rol = Rol(id=4, codigo="CLIENT", nombre="Cliente")
    usuario = Usuario(id=5, email="cliente@test.com", nombre="Cliente", password_hash="hash", roles=[rol], created_at=now_utc, updated_at=now_utc)
    monkeypatch.setattr(auth_router.auth_service, "autenticar", lambda *args, **kwargs: usuario)
    monkeypatch.setattr(auth_router.auth_service, "crear_refresh_token", lambda *args, **kwargs: None)
    monkeypatch.setattr(auth_router, "create_refresh_token_value", lambda: "refresh-test-token")
    client = TestClient(_test_app(usuario))
    response = client.post("/api/v1/auth/login", json={"email": "cliente@test.com", "password": "Password123"})
    assert response.status_code == 200
    assert response.json()["usuario"]["email"] == "cliente@test.com"
    assert "access_token" in response.headers.get("set-cookie", "")
    assert "refresh_token" in response.headers.get("set-cookie", "")


def test_router_query_validation_returns_422(monkeypatch, admin_user):
    client = TestClient(_test_app(admin_user))
    response = client.get("/api/v1/categorias/?page=0")
    assert response.status_code == 422
