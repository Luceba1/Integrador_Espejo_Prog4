import asyncio
from typing import Any

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings
from app.schemas.upload_schema import UploadImagenRead

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024


def _configurar_cloudinary() -> None:
    settings = get_settings()
    if not settings.CLOUDINARY_CLOUD_NAME or not settings.CLOUDINARY_API_KEY or not settings.CLOUDINARY_API_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cloudinary no está configurado. Revisá CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY y CLOUDINARY_API_SECRET en el .env.",
        )

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


def _validar_folder(folder: str | None) -> str:
    settings = get_settings()
    base = (settings.CLOUDINARY_FOLDER or "food_store").strip().strip("/")
    subfolder = (folder or "general").strip().strip("/")
    if not subfolder:
        subfolder = "general"
    subfolder = subfolder.replace("..", "").replace(" ", "_")
    return f"{base}/{subfolder}"


async def subir_imagenes(files: list[UploadFile], folder: str | None = None) -> list[UploadImagenRead]:
    _configurar_cloudinary()

    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debés enviar al menos una imagen.",
        )

    resultados: list[UploadImagenRead] = []
    upload_folder = _validar_folder(folder)

    for file in files:
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"El archivo '{file.filename}' no es una imagen válida. Formatos permitidos: JPG, PNG, WEBP o GIF.",
            )

        contenido = await file.read()
        if len(contenido) > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"El archivo '{file.filename}' supera el límite de 10 MB.",
            )

        upload_result: dict[str, Any] = await asyncio.to_thread(
            cloudinary.uploader.upload,
            contenido,
            folder=upload_folder,
            resource_type="image",
            transformation=[
                {"quality": "auto:good", "fetch_format": "auto"},
            ],
        )

        resultados.append(
            UploadImagenRead(
                public_id=upload_result["public_id"],
                url=upload_result["secure_url"],
                formato=upload_result.get("format"),
                ancho=upload_result.get("width"),
                alto=upload_result.get("height"),
                bytes=upload_result.get("bytes"),
                nombre_archivo=file.filename,
                secure_url=upload_result.get("secure_url"),
                format=upload_result.get("format"),
                width=upload_result.get("width"),
                height=upload_result.get("height"),
                resource_type=upload_result.get("resource_type", "image"),
            )
        )

    return resultados


async def eliminar_imagen(public_id: str) -> None:
    _configurar_cloudinary()

    public_id_limpio = public_id.strip()
    if not public_id_limpio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El public_id es obligatorio.",
        )

    resultado: dict[str, Any] = await asyncio.to_thread(
        cloudinary.uploader.destroy,
        public_id_limpio,
        resource_type="image",
    )

    if resultado.get("result") not in {"ok", "not found"}:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Cloudinary no pudo eliminar la imagen.",
        )
