"""Middlewares transversales de trazabilidad y compatibilidad con ngrok."""

from __future__ import annotations

import time
import uuid

from fastapi import Request


async def add_request_metadata(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{elapsed:.6f}"
    # Evita la pantalla intermedia de ngrok en pruebas locales/demo.
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response
