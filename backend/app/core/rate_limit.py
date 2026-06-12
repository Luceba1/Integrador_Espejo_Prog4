from datetime import datetime, timedelta, timezone
from threading import Lock

from fastapi import HTTPException, Request, status

from app.core.config import get_settings

# Rate limit simple en memoria, suficiente para ejecución local del TPI.
# Limita intentos FALLIDOS por IP en login/register: 5 en 15 minutos.
_failed_attempts: dict[str, list[datetime]] = {}
_lock = Lock()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_auth_rate_limit(request: Request) -> None:
    settings = get_settings()
    ip = _client_ip(request)
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=settings.AUTH_RATE_LIMIT_WINDOW_MINUTES)

    with _lock:
        attempts = [item for item in _failed_attempts.get(ip, []) if item >= window_start]
        _failed_attempts[ip] = attempts

        if len(attempts) >= settings.AUTH_RATE_LIMIT_MAX_ATTEMPTS:
            retry_after = int((attempts[0] + timedelta(minutes=settings.AUTH_RATE_LIMIT_WINDOW_MINUTES) - now).total_seconds())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Demasiados intentos fallidos. Probá nuevamente más tarde.",
                headers={"Retry-After": str(max(1, retry_after))},
            )


def register_failed_auth_attempt(request: Request) -> None:
    ip = _client_ip(request)
    with _lock:
        _failed_attempts.setdefault(ip, []).append(datetime.now(timezone.utc))


def clear_failed_auth_attempts(request: Request) -> None:
    ip = _client_ip(request)
    with _lock:
        _failed_attempts.pop(ip, None)
