from datetime import datetime, timezone

from app.models.rol import Rol
from app.models.unidad_medida import UnidadMedida
from app.models.usuario import Usuario
from app.models.usuario_rol import UsuarioRol
from app.repositories.base_repository import BaseRepository
from app.repositories.rol_repository import RolRepository
from app.repositories.unidad_medida_repository import UnidadMedidaRepository
from app.repositories.usuario_repository import UsuarioRepository


def _create_repository_tables(engine):
    Usuario.__table__.create(engine)
    Rol.__table__.create(engine)
    UsuarioRol.__table__.create(engine)
    UnidadMedida.__table__.create(engine)


def test_base_repository_create_and_get_by_id(sqlite_engine, sqlite_session):
    _create_repository_tables(sqlite_engine)
    repo = BaseRepository(sqlite_session, UnidadMedida)
    unidad = repo.create(UnidadMedida(nombre="Unidad", simbolo="u", tipo="contable"))
    assert unidad.id is not None
    assert repo.get_by_id(unidad.id).nombre == "Unidad"


def test_base_repository_update_persists_changes(sqlite_engine, sqlite_session):
    _create_repository_tables(sqlite_engine)
    repo = BaseRepository(sqlite_session, UnidadMedida)
    unidad = repo.create(UnidadMedida(nombre="Unidad", simbolo="u", tipo="contable"))
    unidad.nombre = "Unidad actualizada"
    updated = repo.update(unidad)
    assert updated.nombre == "Unidad actualizada"


def test_base_repository_hard_delete_removes_entity(sqlite_engine, sqlite_session):
    _create_repository_tables(sqlite_engine)
    repo = BaseRepository(sqlite_session, UnidadMedida)
    unidad = repo.create(UnidadMedida(nombre="Litro", simbolo="L", tipo="volumen"))
    unidad_id = unidad.id
    repo.hard_delete(unidad)
    assert repo.get_by_id(unidad_id) is None


def test_unidad_medida_repository_filters_active_and_deleted(sqlite_engine, sqlite_session):
    _create_repository_tables(sqlite_engine)
    repo = UnidadMedidaRepository(sqlite_session)
    repo.create(UnidadMedida(nombre="Kilogramo", simbolo="kg", tipo="peso"))
    repo.create(UnidadMedida(nombre="Gramo", simbolo="g", tipo="peso", activo=False, deleted_at=datetime.now(timezone.utc)))
    assert [item.simbolo for item in repo.list_active()] == ["kg"]
    assert repo.get_by_simbolo("kg").nombre == "Kilogramo"


def test_rol_repository_get_by_codigo_ignores_deleted_roles(sqlite_engine, sqlite_session):
    _create_repository_tables(sqlite_engine)
    repo = RolRepository(sqlite_session)
    repo.create(Rol(codigo="ADMIN", nombre="Administrador"))
    repo.create(Rol(codigo="OLD", nombre="Viejo", activo=False, deleted_at=datetime.now(timezone.utc)))
    assert repo.get_by_codigo("ADMIN").nombre == "Administrador"
    assert repo.get_by_codigo("OLD") is None


def test_usuario_repository_email_exists_and_active_lookup_normalize_email(sqlite_engine, sqlite_session):
    _create_repository_tables(sqlite_engine)
    repo = UsuarioRepository(sqlite_session)
    usuario = Usuario(email="lucas@test.com", nombre="Lucas", password_hash="hash")
    repo.create(usuario)
    assert repo.email_exists("  LUCAS@test.com  ") is True
    assert repo.get_active_by_email("  LUCAS@test.com  ").id == usuario.id
