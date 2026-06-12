import hmac
import hashlib
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import select

from app.core.config import get_settings
from app.models.pago import Pago
from app.models.usuario import Usuario
from app.schemas.pago_schema import PagoCrearResponse, PagoEstadoResponse
from app.services import pedido_service
from app.services.auth_service import roles_codigos
from app.uow.unit_of_work import SQLModelUnitOfWork

logger = logging.getLogger(__name__)
ROLES_GESTION_PAGOS = {"ADMIN", "PEDIDOS"}


def validar_firma_webhook(headers: dict, query_params: Optional[dict] = None) -> bool:
    """Valida la firma de webhook de MercadoPago cuando MP_WEBHOOK_SECRET está configurado.

    En modo sandbox/local suele no configurarse el secret; en ese caso el webhook
    se acepta para no romper la demo con ngrok. Si está configurado, se valida
    `x-signature` usando `x-request-id` y `data.id`, siguiendo el formato de MP.
    """
    settings = get_settings()
    secret = settings.MP_WEBHOOK_SECRET
    if not secret:
        return True

    x_signature = headers.get("x-signature") or headers.get("X-Signature")
    x_request_id = headers.get("x-request-id") or headers.get("X-Request-Id")
    query_params = query_params or {}
    data_id = query_params.get("data.id") or query_params.get("id")
    if not x_signature or not x_request_id or not data_id:
        return False

    parts = {}
    for part in x_signature.split(","):
        if "=" in part:
            key, value = part.split("=", 1)
            parts[key.strip()] = value.strip()

    ts = parts.get("ts")
    v1 = parts.get("v1")
    if not ts or not v1:
        return False

    manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"
    expected = hmac.new(secret.encode("utf-8"), manifest.encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, v1)

def _tiene_alguno(usuario: Usuario, roles: set[str]) -> bool:
    return bool(set(roles_codigos(usuario)).intersection(roles))


def _validar_visibilidad_pedido(pedido, usuario: Usuario) -> None:
    if pedido.usuario_id != usuario.id and not _tiene_alguno(usuario, ROLES_GESTION_PAGOS):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permisos para operar pagos de este pedido.",
        )


def _crear_preferencia_mp(monto: float, titulo: str, pedido_id: int, back_urls: dict) -> dict:
    settings = get_settings()
    access_token = settings.MP_ACCESS_TOKEN
    if not access_token:
        raise RuntimeError("MercadoPago no está configurado. Configure MP_ACCESS_TOKEN")

    try:
        import mercadopago

        sdk = mercadopago.SDK(access_token)
        public_base_url = settings.NGROK_URL or settings.VITE_API_URL or "http://localhost:8000"
        notification_url = settings.MP_WEBHOOK_URL or f"{public_base_url.rstrip('/')}/api/v1/pagos/webhook"

        preference_data = {
            "items": [
                {
                    "title": titulo,
                    "quantity": 1,
                    "unit_price": float(monto),
                    "currency_id": "ARS",
                }
            ],
            "external_reference": str(pedido_id),
            "metadata": {"pedido_id": pedido_id},
            "back_urls": back_urls,
            "notification_url": notification_url,
            "auto_return": "approved",
        }

        result = sdk.preference().create(preference_data)

        if result.get("status") not in (200, 201):
            logger.error("Error creando preferencia MP: %s", result)
            raise RuntimeError(
                f"Error al crear preferencia: {result.get('response', {}).get('message', 'desconocido')}"
            )

        response = result.get("response", {})
        return {
            "preference_id": response.get("id"),
            "init_point": response.get("init_point"),
            "sandbox_init_point": response.get("sandbox_init_point"),
        }

    except ImportError:
        raise RuntimeError("Falta instalar el SDK: pip install mercadopago")
    except Exception as e:
        logger.exception("Error inesperado al crear preferencia MP")
        raise RuntimeError(f"Error de conexión con MP: {str(e)}")


def _consultar_pago_mp(payment_id: int) -> dict:
    settings = get_settings()
    access_token = settings.MP_ACCESS_TOKEN
    if not access_token:
        raise RuntimeError("MercadoPago no está configurado.")

    try:
        import mercadopago

        sdk = mercadopago.SDK(access_token)
        result = sdk.payment().get(payment_id)

        if result.get("status") != 200:
            logger.error("Error consultando pago MP %s: %s", payment_id, result)
            raise RuntimeError(f"Error al consultar pago {payment_id}")

        response = result.get("response", {})
        return {
            "mp_payment_id": response.get("id"),
            "mp_status": response.get("status"),
            "mp_status_detail": response.get("status_detail"),
            "mp_merchant_order_id": response.get("merchant_order_id"),
            "external_reference": response.get("external_reference"),
            "transaction_amount": response.get("transaction_amount"),
            "payment_method_id": response.get("payment_method_id"),
        }

    except ImportError:
        raise RuntimeError("Falta instalar el SDK: pip install mercadopago")
    except Exception as e:
        logger.exception("Error consultando pago MP %s", payment_id)
        raise RuntimeError(f"Error de conexión con MP: {str(e)}")


def _mapear_estado_mp(estado_mp: str | None) -> str | None:
    if estado_mp == "approved":
        return "aprobado"
    if estado_mp in ("rejected", "cancelled", "refunded", "charged_back"):
        return "rechazado"
    if estado_mp in ("pending", "in_process", "authorized"):
        return "pendiente"
    return None


def _ultimo_pago_por_pedido(uow: SQLModelUnitOfWork, pedido_id: int) -> Pago | None:
    stmt = select(Pago).where(Pago.pedido_id == pedido_id).order_by(Pago.created_at.desc())
    return uow.session.exec(stmt).first()


def _buscar_pago_local(uow: SQLModelUnitOfWork, pago_mp_id: int, mp_info: dict) -> Pago | None:
    stmt = select(Pago).where(Pago.mp_payment_id == pago_mp_id)
    pago = uow.session.exec(stmt).first()

    if not pago and mp_info.get("mp_merchant_order_id"):
        stmt_merchant = select(Pago).where(Pago.mp_merchant_order_id == mp_info["mp_merchant_order_id"])
        pago = uow.session.exec(stmt_merchant).first()

    if not pago and mp_info.get("external_reference"):
        try:
            pedido_id = int(mp_info["external_reference"])
        except (TypeError, ValueError):
            pedido_id = None
        if pedido_id:
            pago = _ultimo_pago_por_pedido(uow, pedido_id)

    return pago


def _actualizar_pago_desde_mp(pago: Pago, pago_mp_id: int, mp_info: dict, nuevo_estado: str) -> None:
    pago.mp_payment_id = int(pago_mp_id)
    pago.mp_status = mp_info.get("mp_status")
    pago.mp_status_detail = mp_info.get("mp_status_detail")
    pago.mp_merchant_order_id = mp_info.get("mp_merchant_order_id")
    if mp_info.get("transaction_amount") is not None:
        pago.transaction_amount = mp_info.get("transaction_amount")
    pago.payment_method_id = mp_info.get("payment_method_id")
    pago.external_reference = mp_info.get("external_reference") or pago.external_reference
    pago.estado = nuevo_estado
    pago.updated_at = datetime.now(timezone.utc)


def crear_pago(uow: SQLModelUnitOfWork, usuario: Usuario, pedido_id: int) -> PagoCrearResponse:
    settings = get_settings()

    pedido = uow.pedidos.get_active_with_details(pedido_id)
    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado.")
    _validar_visibilidad_pedido(pedido, usuario)

    if pedido.estado_codigo != pedido_service.ESTADO_INICIAL:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se puede pagar un pedido pendiente.",
        )

    if pedido.forma_pago_codigo != "MERCADOPAGO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este pedido no fue creado con MercadoPago como forma de pago.",
        )

    if not settings.MP_ACCESS_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MercadoPago no configurado. Configure MP_ACCESS_TOKEN",
        )

    backend_url = settings.NGROK_URL or settings.VITE_API_URL or "http://localhost:8000"
    backend_url = backend_url.rstrip("/")
    back_urls = {
        "success": f"{backend_url}/api/v1/pagos/redirect/{pedido_id}/success",
        "failure": f"{backend_url}/api/v1/pagos/redirect/{pedido_id}/failure",
        "pending": f"{backend_url}/api/v1/pagos/redirect/{pedido_id}/pending",
    }

    try:
        mp_data = _crear_preferencia_mp(
            monto=float(pedido.total),
            titulo=f"Pedido #{pedido_id} - Food Store",
            pedido_id=pedido_id,
            back_urls=back_urls,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    pago = Pago(
        pedido_id=pedido_id,
        monto=pedido.total,
        estado="pendiente",
        mp_preference_id=mp_data["preference_id"],
        mp_init_point=mp_data.get("init_point") or mp_data.get("sandbox_init_point"),
        transaction_amount=pedido.total,
        external_reference=str(pedido_id),
        idempotency_key=str(uuid.uuid4()),
    )
    uow.session.add(pago)
    uow.session.flush()

    return PagoCrearResponse(
        pago_id=pago.id,
        preference_id=mp_data["preference_id"],
        init_point=mp_data.get("init_point"),
        sandbox_init_point=mp_data.get("sandbox_init_point"),
        public_key=settings.MP_PUBLIC_KEY,
    )


def _extraer_payment_id_webhook(data: dict, query_params: Optional[dict] = None) -> tuple[str | None, str | None]:
    """Extrae de forma segura el tipo de evento y el ID real del pago.

    MercadoPago puede enviar varias formas de notificación:
    - ?type=payment&data.id=123
    - ?topic=payment&id=123
    - body: {"type": "payment", "data": {"id": "123"}}
    - body: {"topic": "payment", "resource": ".../v1/payments/123"}

    Importante: algunas notificaciones traen un campo body.id que NO es el
    payment_id, sino el id de la notificación. Por eso se prioriza siempre
    query_params["data.id"] y data["data"]["id"].
    """
    query_params = query_params or {}
    data = data or {}

    topic = (
        query_params.get("type")
        or query_params.get("topic")
        or data.get("type")
        or data.get("topic")
    )

    # Si MercadoPago avisa una merchant_order, no debemos consultarla como pago.
    if topic and topic != "payment":
        return topic, None

    nested_data = data.get("data") if isinstance(data.get("data"), dict) else {}
    payment_id = (
        query_params.get("data.id")
        or nested_data.get("id")
        or data.get("data_id")
    )

    # Formato legacy: topic=payment&id=<payment_id>. Solo usamos id si sabemos que es payment.
    if not payment_id and topic == "payment":
        payment_id = query_params.get("id")

    # Otro formato legacy: {resource: "https://api.mercadopago.com/v1/payments/<id>"}
    resource = data.get("resource")
    if not payment_id and topic == "payment" and isinstance(resource, str) and "/payments/" in resource:
        payment_id = resource.rstrip("/").split("/")[-1]

    # Último fallback: body.id solo si el evento declara explícitamente type/topic=payment
    # y no llegó otro identificador más confiable.
    if not payment_id and topic == "payment":
        payment_id = data.get("id")

    return topic, str(payment_id) if payment_id is not None else None


def procesar_webhook(uow: SQLModelUnitOfWork, data: dict, query_params: Optional[dict] = None) -> dict:
    logger.info("Webhook recibido: data=%s qs=%s", data, query_params or {})

    topic, pago_mp_id = _extraer_payment_id_webhook(data, query_params)

    if topic and topic != "payment":
        return {"status": "ignored", "reason": f"Topic: {topic}"}
    if not pago_mp_id:
        return {"status": "ignored", "reason": "No payment ID"}

    try:
        mp_info = _consultar_pago_mp(int(pago_mp_id))
        nuevo_estado = _mapear_estado_mp(mp_info.get("mp_status"))
        if nuevo_estado is None:
            return {"status": "ignored", "reason": f"Unknown status: {mp_info.get('mp_status')}"}

        pago = _buscar_pago_local(uow, int(pago_mp_id), mp_info)
        if not pago:
            return {"status": "ignored", "reason": "Pago not found in local DB"}

        estado_anterior = pago.estado
        if pago.estado == nuevo_estado and pago.mp_payment_id == int(pago_mp_id):
            pedido = uow.pedidos.get_active_with_details(pago.pedido_id)
            return {
                "status": "already_processed",
                "estado": pago.estado,
                "pedido_id": pago.pedido_id,
                "pedido_estado": pedido.estado_codigo if pedido else None,
            }

        _actualizar_pago_desde_mp(pago, int(pago_mp_id), mp_info, nuevo_estado)
        uow.session.add(pago)

        if nuevo_estado == "aprobado":
            pedido_service.confirmar_por_pago(uow, pago.pedido_id)

        pedido = uow.pedidos.get_active_with_details(pago.pedido_id)
        return {
            "status": "processed",
            "pago_id": pago.id,
            "estado_anterior": estado_anterior,
            "estado": nuevo_estado,
            "pedido_id": pago.pedido_id,
            "pedido_estado": pedido.estado_codigo if pedido else None,
        }

    except Exception as e:
        logger.exception("Error procesando webhook MP")
        return {"status": "error", "reason": str(e)}


def confirmar_pago(
    uow: SQLModelUnitOfWork,
    usuario: Usuario,
    pedido_id: int,
    payment_id: Optional[int] = None,
) -> PagoEstadoResponse:
    pedido = uow.pedidos.get_active_with_details(pedido_id)
    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    _validar_visibilidad_pedido(pedido, usuario)

    resolved_payment_id = payment_id
    pago_local = _ultimo_pago_por_pedido(uow, pedido_id)

    if not resolved_payment_id and pago_local and pago_local.mp_payment_id:
        resolved_payment_id = pago_local.mp_payment_id

    if resolved_payment_id:
        try:
            mp_info = _consultar_pago_mp(resolved_payment_id)
        except RuntimeError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        nuevo_estado = _mapear_estado_mp(mp_info.get("mp_status")) or "pendiente"

        if pago_local:
            _actualizar_pago_desde_mp(pago_local, resolved_payment_id, mp_info, nuevo_estado)
            uow.session.add(pago_local)

            if nuevo_estado == "aprobado":
                pedido_service.confirmar_por_pago(uow, pedido_id, usuario_id=None, motivo="Pago confirmado por retorno de MercadoPago.")

        pedido_actualizado = uow.pedidos.get_active_with_details(pedido_id)
        return PagoEstadoResponse(
            estado=nuevo_estado,
            pedido_id=pedido_id,
            pedido_estado=pedido_actualizado.estado_codigo if pedido_actualizado else pedido.estado_codigo,
        )

    return PagoEstadoResponse(
        estado=pago_local.estado if pago_local else None,
        pedido_id=pedido_id,
        pedido_estado=pedido.estado_codigo,
    )
