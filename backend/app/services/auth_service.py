from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.core.security import hash_password, verify_password, hash_refresh_token, refresh_token_expiration
from app.models.refresh_token import RefreshToken
from app.models.usuario import Usuario
from app.schemas.auth_schema import LoginRequest, UsuarioRegister
from app.uow.unit_of_work import SQLModelUnitOfWork

ROL_CLIENTE = "CLIENT"

def _as_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def _normalizar_email(email: str) -> str:
    return email.lower().strip()


def _roles_codigos(usuario: Usuario) -> list[str]:
    return [rol.codigo for rol in usuario.roles if rol.activo]


def registrar_cliente(uow: SQLModelUnitOfWork, payload: UsuarioRegister) -> Usuario:
    email = _normalizar_email(str(payload.email))
    if uow.usuarios.email_exists(email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario registrado con ese email.",
        )

    rol_cliente = uow.roles.get_by_codigo(ROL_CLIENTE)
    if rol_cliente is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No existe el rol CLIENT. Ejecutá el seed obligatorio.",
        )

    usuario = Usuario(
        email=email,
        nombre=payload.nombre.strip(),
        apellido=payload.apellido.strip() if payload.apellido else None,
        password_hash=hash_password(payload.password),
    )
    usuario.roles = [rol_cliente]

    try:
        return uow.usuarios.create(usuario)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo registrar el usuario.",
        ) from exc


def autenticar(uow: SQLModelUnitOfWork, payload: LoginRequest) -> Usuario:
    usuario = uow.usuarios.get_active_by_email(_normalizar_email(str(payload.email)))
    if usuario is None or not verify_password(payload.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos.",
        )
    return usuario


def obtener_usuario_actual(uow: SQLModelUnitOfWork, usuario_id: int) -> Usuario:
    usuario = uow.usuarios.get_active_by_id(usuario_id)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autenticado.",
        )
    return usuario


def crear_refresh_token(uow: SQLModelUnitOfWork, usuario_id: int, token: str) -> RefreshToken:
    refresh = RefreshToken(
        usuario_id=usuario_id,
        token_hash=hash_refresh_token(token),
        expires_at=refresh_token_expiration(),
    )
    uow.session.add(refresh)
    uow.session.flush()
    return refresh


def obtener_usuario_por_refresh_token(uow: SQLModelUnitOfWork, token: str) -> Usuario:
    token_hash = hash_refresh_token(token)
    refresh = uow.session.exec(select(RefreshToken).where(RefreshToken.token_hash == token_hash)).first()
    expires_at = _as_utc(refresh.expires_at) if refresh else None
    revoked_at = _as_utc(refresh.revoked_at) if refresh else None
    now = datetime.now(timezone.utc)
    if refresh is None or revoked_at is not None or expires_at is None or expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o vencido.",
        )
    usuario = obtener_usuario_actual(uow, refresh.usuario_id)
    return usuario


def revocar_refresh_token(uow: SQLModelUnitOfWork, token: str | None) -> None:
    if not token:
        return
    token_hash = hash_refresh_token(token)
    refresh = uow.session.exec(select(RefreshToken).where(RefreshToken.token_hash == token_hash)).first()
    if refresh is None or refresh.revoked_at is not None:
        return
    refresh.revoked_at = datetime.now(timezone.utc)
    uow.session.add(refresh)
    uow.session.flush()


def rotar_refresh_token(uow: SQLModelUnitOfWork, old_token: str, new_token: str, usuario_id: int) -> None:
    revocar_refresh_token(uow, old_token)
    crear_refresh_token(uow, usuario_id, new_token)


def roles_codigos(usuario: Usuario) -> list[str]:
    return _roles_codigos(usuario)
