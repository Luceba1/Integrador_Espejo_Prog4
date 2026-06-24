"""Handlers globales de error con formato simple tipo RFC 7807.

El TPI pide respuestas de error uniformes con `detail`, `code` y `field`.
Este módulo centraliza ese formato para HTTPException, errores de validación
Pydantic/FastAPI y errores de base de datos.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger("app.core.exceptions")


def problem_detail(detail: str, code: str, field: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"detail": detail, "code": code}
    if field:
        payload["field"] = field
    return payload


def _first_validation_error(exc: RequestValidationError) -> tuple[str, str | None]:
    errors = exc.errors()
    if not errors:
        return "Solicitud inválida.", None

    first = errors[0]
    loc = first.get("loc") or []
    # Omitimos la primera parte típica: body/query/path.
    field = ".".join(str(item) for item in loc[1:]) if len(loc) > 1 else None
    message = str(first.get("msg") or "Valor inválido.")

    # Evitamos mostrar mensajes técnicos de Pydantic/email-validator al usuario.
    # Ejemplo anterior: "email: value is not a valid email address..."
    if field == "email":
        return "Ingresá un email válido.", field

    if field:
        return f"{field}: {message}", field
    return message, None


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    body = problem_detail(detail=detail, code=f"HTTP_{exc.status_code}")
    return JSONResponse(status_code=exc.status_code, content=body, headers=exc.headers or None)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    detail, field = _first_validation_error(exc)
    body = problem_detail(detail=detail, code="VALIDATION_ERROR", field=field)
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=body)


async def integrity_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    logger.exception("Error de integridad de base de datos")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=problem_detail(
            detail="La operación viola una restricción de integridad o unicidad.",
            code="DATABASE_INTEGRITY_ERROR",
        ),
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("Error de base de datos")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=problem_detail(detail="Error interno de base de datos.", code="DATABASE_ERROR"),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Error inesperado")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=problem_detail(detail="Error interno del servidor.", code="INTERNAL_SERVER_ERROR"),
    )
