from typing import Annotated

from fastapi import APIRouter, Body, Cookie, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth_dependencies import get_current_user
from app.core.config import get_settings
from app.core.rate_limit import check_auth_rate_limit, clear_failed_auth_attempts, register_failed_auth_attempt
from app.core.security import create_access_token, create_refresh_token_value
from app.models.usuario import Usuario
from app.schemas.auth_schema import AuthResponse, LoginRequest, LogoutRequest, RefreshTokenRequest, TokenResponse, UsuarioRead, UsuarioRegister
from app.services import auth_service
from app.uow.unit_of_work import SQLModelUnitOfWork, get_uow

router = APIRouter(prefix="/auth", tags=["Autenticación"])

UowDep = Annotated[SQLModelUnitOfWork, Depends(get_uow)]
CurrentUserDep = Annotated[Usuario, Depends(get_current_user)]


def _auth_response(
    usuario: Usuario,
    access_token: str | None = None,
    refresh_token: str | None = None,
) -> AuthResponse:
    settings = get_settings()
    return AuthResponse(
        usuario=UsuarioRead.model_validate(usuario),
        roles=auth_service.roles_codigos(usuario),
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def _build_access_token(usuario: Usuario) -> str:
    return create_access_token(
        subject=str(usuario.id),
        extra_claims={"roles": auth_service.roles_codigos(usuario)},
    )


def _set_access_cookie(response: Response, usuario: Usuario, token: str | None = None) -> str:
    settings = get_settings()
    token = token or _build_access_token(usuario)
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/",
    )
    return token


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path="/api/v1/auth",
    )


def _crear_sesion(response: Response, uow: SQLModelUnitOfWork, usuario: Usuario) -> tuple[str, str]:
    access_token = _set_access_cookie(response, usuario)
    refresh_token = create_refresh_token_value()
    auth_service.crear_refresh_token(uow, usuario.id, refresh_token)
    _set_refresh_cookie(response, refresh_token)
    return access_token, refresh_token


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def registrar(payload: UsuarioRegister, request: Request, response: Response, uow: UowDep) -> AuthResponse:
    check_auth_rate_limit(request)
    try:
        usuario = auth_service.registrar_cliente(uow, payload)
    except Exception:
        register_failed_auth_attempt(request)
        raise
    clear_failed_auth_attempts(request)
    access_token, refresh_token = _crear_sesion(response, uow, usuario)
    return _auth_response(usuario, access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def login(payload: LoginRequest, request: Request, response: Response, uow: UowDep) -> AuthResponse:
    check_auth_rate_limit(request)
    try:
        usuario = auth_service.autenticar(uow, payload)
    except Exception:
        register_failed_auth_attempt(request)
        raise
    clear_failed_auth_attempts(request)
    access_token, refresh_token = _crear_sesion(response, uow, usuario)
    return _auth_response(usuario, access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def refresh(
    response: Response,
    uow: UowDep,
    payload: Annotated[RefreshTokenRequest | None, Body()] = None,
    refresh_token_cookie: Annotated[str | None, Cookie(alias="refresh_token")] = None,
) -> AuthResponse:
    # El TPI documenta refresh_token por body; el frontend usa cookie HttpOnly.
    # Soportamos ambos, priorizando body cuando llega explícito.
    refresh_token = (payload.refresh_token if payload else None) or refresh_token_cookie or ""
    usuario = auth_service.obtener_usuario_por_refresh_token(uow, refresh_token)
    nuevo_refresh = create_refresh_token_value()
    auth_service.rotar_refresh_token(uow, refresh_token, nuevo_refresh, usuario.id)
    access_token = _set_access_cookie(response, usuario)
    _set_refresh_cookie(response, nuevo_refresh)
    return _auth_response(usuario, access_token=access_token, refresh_token=nuevo_refresh)


@router.post("/token", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def token_oauth2_compatible(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    response: Response,
    uow: UowDep,
) -> TokenResponse:
    """Login compatible con OAuth2PasswordRequestForm para Swagger/REST Client."""

    check_auth_rate_limit(request)
    try:
        usuario = auth_service.autenticar(
            uow,
            LoginRequest(email=form_data.username, password=form_data.password),
        )
    except Exception:
        register_failed_auth_attempt(request)
        raise
    clear_failed_auth_attempts(request)
    access_token, refresh_token = _crear_sesion(response, uow, usuario)
    settings = get_settings()
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        usuario=UsuarioRead.model_validate(usuario),
        roles=auth_service.roles_codigos(usuario),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    uow: UowDep,
    payload: Annotated[LogoutRequest | None, Body()] = None,
    refresh_token_cookie: Annotated[str | None, Cookie(alias="refresh_token")] = None,
) -> Response:
    refresh_token = (payload.refresh_token if payload else None) or refresh_token_cookie
    auth_service.revocar_refresh_token(uow, refresh_token)
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/api/v1/auth")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def me(usuario: CurrentUserDep) -> AuthResponse:
    return _auth_response(usuario)
