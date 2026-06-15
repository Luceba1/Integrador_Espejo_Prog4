from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException


from app.core.config import get_settings
from app.core.db import create_db_and_tables
from app.core.exceptions import (
    http_exception_handler,
    integrity_exception_handler,
    sqlalchemy_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.request_middleware import add_request_metadata
from app.db.seed import run_seed
from app.routers.auth_router import router as auth_router
from app.routers.admin_router import router as admin_router
from app.routers.categoria_router import router as categoria_router
from app.routers.direccion_router import router as direccion_router
from app.routers.ingrediente_router import router as ingrediente_router
from app.routers.producto_router import router as producto_router
from app.routers.pedido_router import router as pedido_router
from app.routers.kds_router import router as kds_router
from app.routers.pago_router import router as pago_router
from app.routers.upload_router import router as upload_router
from app.routers.unidad_medida_router import router as unidad_medida_router
from app.routers.ws_router import router as ws_router
from app.routers.export_router import router as export_router
from app.routers.estadistica_router import router as estadistica_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    run_seed()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

# CORS para permitir que el frontend Vite se conecte a la API.
# Importante: Content-Type y Authorization deben estar permitidos para login y rutas protegidas.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.middleware("http")(add_request_metadata)

# Handlers globales estilo Problem Details / RFC 7807 simplificado.
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


# Rutas oficiales pedidas por Parcial 2
app.include_router(auth_router, prefix="/api/v1")
app.include_router(categoria_router, prefix="/api/v1")
app.include_router(ingrediente_router, prefix="/api/v1")
app.include_router(producto_router, prefix="/api/v1")
app.include_router(direccion_router, prefix="/api/v1")
app.include_router(pedido_router, prefix="/api/v1")
app.include_router(kds_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(pago_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")
app.include_router(unidad_medida_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/api/v1")
app.include_router(ws_router)  # Alias TPI: /ws/... además de /api/v1/ws/...
app.include_router(export_router, prefix="/api/v1")
app.include_router(estadistica_router, prefix="/api/v1")

# Compatibilidad temporal con el frontend del Parcial 1 aprobado.
# Cuando el frontend migre a axios, se consumen las rutas /api/v1.
app.include_router(categoria_router)
app.include_router(ingrediente_router)
app.include_router(producto_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "API del parcial 2 funcionando."}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
