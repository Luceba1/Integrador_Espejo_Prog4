from sqlmodel import Session, SQLModel

from app.core.config import Settings, get_settings
from app.core import db
from app.models.rol import Rol
from app.models.unidad_medida import UnidadMedida


def test_settings_parse_cors_origins_from_csv_string():
    settings = Settings(
        DATABASE_URL="sqlite:///./x.db",
        SECRET_KEY="secret",
        BACKEND_CORS_ORIGINS="http://a.test,http://b.test",
    )
    assert settings.BACKEND_CORS_ORIGINS == ["http://a.test", "http://b.test"]


def test_get_settings_is_cached_instance():
    first = get_settings()
    second = get_settings()
    assert first is second


def test_database_engine_uses_configured_url():
    assert "sqlite" in str(db.engine.url)


def test_get_session_yields_sqlmodel_session():
    generator = db.get_session()
    session = next(generator)
    try:
        assert isinstance(session, Session)
        assert session.bind is db.engine
    finally:
        generator.close()


def test_selected_model_tables_can_be_created_in_isolated_sqlite(sqlite_engine):
    UnidadMedida.__table__.create(sqlite_engine)
    Rol.__table__.create(sqlite_engine)
    assert "unidad_medida" in SQLModel.metadata.tables
    assert "rol" in SQLModel.metadata.tables
