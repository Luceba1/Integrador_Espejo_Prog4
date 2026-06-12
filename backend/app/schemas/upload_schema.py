from pydantic import BaseModel, ConfigDict


class UploadImagenRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: str
    url: str
    formato: str | None = None
    ancho: int | None = None
    alto: int | None = None
    bytes: int | None = None
    nombre_archivo: str | None = None
    # Aliases compatibles con la especificación TPI / CloudinaryResponse.
    secure_url: str | None = None
    format: str | None = None
    width: int | None = None
    height: int | None = None
    resource_type: str | None = "image"


class UploadDeletePayload(BaseModel):
    public_id: str
