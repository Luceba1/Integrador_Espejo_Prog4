from typing import Annotated

from fastapi import APIRouter, Depends, File, Path, Query, Response, UploadFile, status

from app.core.auth_dependencies import require_roles
from app.models.usuario import Usuario
from app.schemas.upload_schema import UploadDeletePayload, UploadImagenRead
from app.services import upload_service

router = APIRouter(prefix="/uploads", tags=["Uploads"])
AdminStockDep = Annotated[Usuario, Depends(require_roles("ADMIN", "STOCK"))]


@router.post("/imagenes", response_model=list[UploadImagenRead], status_code=status.HTTP_201_CREATED)
async def subir_imagenes(
    _usuario: AdminStockDep,
    files: Annotated[list[UploadFile], File(description="Una o más imágenes para subir a Cloudinary.")],
    folder: Annotated[str | None, Query(max_length=80)] = "general",
) -> list[UploadImagenRead]:
    return await upload_service.subir_imagenes(files, folder=folder)


@router.post("/imagen", response_model=UploadImagenRead, status_code=status.HTTP_201_CREATED)
async def subir_imagen_tpi(
    _usuario: AdminStockDep,
    file: Annotated[UploadFile, File(description="Imagen para subir a Cloudinary.")],
    folder: Annotated[str | None, Query(max_length=80)] = "general",
) -> UploadImagenRead:
    """Alias compatible con la especificación del TPI para una sola imagen."""
    resultados = await upload_service.subir_imagenes([file], folder=folder)
    return resultados[0]


@router.delete("/imagenes", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_imagen(payload: UploadDeletePayload, _usuario: AdminStockDep) -> Response:
    await upload_service.eliminar_imagen(payload.public_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/imagen/{public_id:path}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_imagen_tpi(
    public_id: Annotated[str, Path(min_length=1)],
    _usuario: AdminStockDep,
) -> Response:
    """Alias compatible con la especificación del TPI."""
    await upload_service.eliminar_imagen(public_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
