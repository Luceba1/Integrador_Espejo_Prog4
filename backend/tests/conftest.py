"""Configuración común de tests.

Los tests usan configuración aislada y no dependen de la base PostgreSQL local.
Se tomó como referencia el enfoque del ejemplo api_middlewares_testing:
pytest.ini + conftest.py + tests separados por capa.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest
from sqlmodel import Session, create_engine

# Deben setearse antes de importar app.core.config / app.core.db.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_food_store.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")
os.environ.setdefault("AUTH_RATE_LIMIT_MAX_ATTEMPTS", "5")
os.environ.setdefault("AUTH_RATE_LIMIT_WINDOW_MINUTES", "15")
os.environ.setdefault("BACKEND_CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
os.environ.setdefault("COOKIE_SECURE", "false")
os.environ.setdefault("COOKIE_SAMESITE", "lax")


@pytest.fixture
def now_utc() -> datetime:
    return datetime.now(timezone.utc)


@pytest.fixture
def sqlite_engine():
    """Engine SQLite temporal para tests de repositorios simples.

    No se llama SQLModel.metadata.create_all() porque algunos modelos usan tipos
    PostgreSQL específicos como ARRAY/JSONB. Cada test crea solo las tablas que necesita.
    """

    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    return engine


@pytest.fixture
def sqlite_session(sqlite_engine):
    with Session(sqlite_engine) as session:
        yield session


class DummyRepo:
    def __init__(self, items=None):
        self.items = list(items or [])
        self.created = []
        self.updated = []
        self.deleted = []
        self.by_id = {}
        for item in self.items:
            if getattr(item, "id", None) is not None:
                self.by_id[item.id] = item

    def list_paginated(self, **kwargs):
        self.last_kwargs = kwargs
        return self.items

    def list_all_without_pagination(self, **kwargs):
        self.last_kwargs = kwargs
        return self.items

    def list_active(self):
        return [item for item in self.items if getattr(item, "activo", True)]

    def get_by_id(self, entity_id: int):
        return self.by_id.get(entity_id)

    def get_active_by_id(self, entity_id: int):
        item = self.by_id.get(entity_id)
        if item is None or not getattr(item, "activo", True) or getattr(item, "deleted_at", None) is not None:
            return None
        return item

    def get_by_codigo(self, codigo: str):
        for item in self.items:
            if getattr(item, "codigo", None) == codigo and getattr(item, "activo", True):
                return item
        return None

    def get_by_simbolo(self, simbolo: str):
        for item in self.items:
            if getattr(item, "simbolo", None) == simbolo:
                return item
        return None

    def nombre_exists(self, nombre: str, exclude_id=None):
        return any(
            getattr(item, "nombre", "").lower() == nombre.lower()
            and getattr(item, "id", None) != exclude_id
            and getattr(item, "activo", True)
            and getattr(item, "deleted_at", None) is None
            for item in self.items
        )

    def email_exists(self, email: str):
        return any(getattr(item, "email", "").lower().strip() == email.lower().strip() for item in self.items)

    def get_active_by_email(self, email: str):
        for item in self.items:
            if getattr(item, "email", "").lower().strip() == email.lower().strip() and getattr(item, "activo", True):
                return item
        return None

    def create(self, entity):
        if getattr(entity, "id", None) is None:
            entity.id = len(self.created) + len(self.items) + 1
        self.created.append(entity)
        self.items.append(entity)
        self.by_id[entity.id] = entity
        return entity

    def update(self, entity):
        self.updated.append(entity)
        if getattr(entity, "id", None) is not None:
            self.by_id[entity.id] = entity
        return entity

    def hard_delete(self, entity):
        self.deleted.append(entity)
        if entity in self.items:
            self.items.remove(entity)


@pytest.fixture
def dummy_uow():
    return SimpleNamespace()


@pytest.fixture
def admin_user(now_utc):
    from app.models.rol import Rol
    from app.models.usuario import Usuario

    return Usuario(
        id=1,
        email="admin@test.com",
        nombre="Admin",
        apellido="Test",
        password_hash="hash",
        roles=[Rol(id=1, codigo="ADMIN", nombre="Administrador")],
        created_at=now_utc,
        updated_at=now_utc,
    )


@pytest.fixture
def client_user(now_utc):
    from app.models.rol import Rol
    from app.models.usuario import Usuario

    return Usuario(
        id=2,
        email="cliente@test.com",
        nombre="Cliente",
        apellido="Test",
        password_hash="hash",
        roles=[Rol(id=4, codigo="CLIENT", nombre="Cliente")],
        created_at=now_utc,
        updated_at=now_utc,
    )


@pytest.fixture
def unidad(now_utc):
    from app.models.unidad_medida import UnidadMedida

    return UnidadMedida(
        id=1,
        nombre="Unidad",
        simbolo="u",
        tipo="contable",
        activo=True,
        created_at=now_utc,
        updated_at=now_utc,
    )


@pytest.fixture
def categoria(now_utc):
    from app.models.categoria import Categoria

    return Categoria(
        id=1,
        nombre="Bebidas",
        descripcion="Bebidas frías",
        activo=True,
        created_at=now_utc,
        updated_at=now_utc,
    )


@pytest.fixture
def precio_decimal():
    return Decimal("10.50")
