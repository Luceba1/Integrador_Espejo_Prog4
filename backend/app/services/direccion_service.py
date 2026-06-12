from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.direccion_entrega import DireccionEntrega
from app.models.usuario import Usuario
from app.schemas.direccion_schema import DireccionCreate, DireccionUpdate
from app.uow.unit_of_work import SQLModelUnitOfWork


def listar(uow: SQLModelUnitOfWork, usuario: Usuario) -> list[DireccionEntrega]:
    return uow.direcciones.list_active_by_user(usuario.id)


def obtener_por_id(uow: SQLModelUnitOfWork, usuario: Usuario, direccion_id: int) -> DireccionEntrega:
    direccion = uow.direcciones.get_active_by_id_for_user(direccion_id, usuario.id)
    if direccion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dirección de entrega no encontrada.",
        )
    return direccion


def crear(uow: SQLModelUnitOfWork, usuario: Usuario, payload: DireccionCreate) -> DireccionEntrega:
    data = payload.model_dump()
    es_principal_solicitada = data.pop("es_principal", False)
    debe_ser_principal = es_principal_solicitada or not uow.direcciones.user_has_active_addresses(usuario.id)

    if debe_ser_principal:
        uow.direcciones.unset_principal_for_user(usuario.id)

    direccion = DireccionEntrega(
        **data,
        usuario_id=usuario.id,
        es_principal=debe_ser_principal,
    )

    try:
        return uow.direcciones.create(direccion)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear la dirección de entrega.",
        ) from exc


def actualizar(
    uow: SQLModelUnitOfWork,
    usuario: Usuario,
    direccion_id: int,
    payload: DireccionUpdate,
) -> DireccionEntrega:
    direccion = obtener_por_id(uow, usuario, direccion_id)
    cambios = payload.model_dump(exclude_unset=True)

    for campo, valor in cambios.items():
        setattr(direccion, campo, valor)

    direccion.updated_at = datetime.now(timezone.utc)

    try:
        return uow.direcciones.update(direccion)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo actualizar la dirección de entrega.",
        ) from exc


def marcar_principal(uow: SQLModelUnitOfWork, usuario: Usuario, direccion_id: int) -> DireccionEntrega:
    direccion = obtener_por_id(uow, usuario, direccion_id)
    uow.direcciones.unset_principal_for_user(usuario.id)
    direccion.es_principal = True
    direccion.updated_at = datetime.now(timezone.utc)
    return uow.direcciones.update(direccion)


def eliminar(uow: SQLModelUnitOfWork, usuario: Usuario, direccion_id: int) -> None:
    direccion = obtener_por_id(uow, usuario, direccion_id)
    direccion.activo = False
    direccion.es_principal = False
    direccion.deleted_at = datetime.now(timezone.utc)
    direccion.updated_at = direccion.deleted_at
    uow.direcciones.update(direccion)

    principal = uow.direcciones.get_principal_by_user(usuario.id)
    if principal is None:
        restantes = uow.direcciones.list_active_by_user(usuario.id)
        if restantes:
            restantes[0].es_principal = True
            restantes[0].updated_at = datetime.now(timezone.utc)
            uow.direcciones.update(restantes[0])
