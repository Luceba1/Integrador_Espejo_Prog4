from app.core.config import get_settings
from app.services import upload_service


def test_uploads_functional_sanitizes_cloudinary_folder(monkeypatch):
    monkeypatch.setenv("CLOUDINARY_FOLDER", "food_store")
    get_settings.cache_clear()
    try:
        assert upload_service._validar_folder(" productos destacados ") == "food_store/productos_destacados"
        assert upload_service._validar_folder("../secret") == "food_store/secret"
    finally:
        get_settings.cache_clear()
