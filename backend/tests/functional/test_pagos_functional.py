import sys
import types

from app.core.config import get_settings
from app.services import pago_service


def test_pagos_functional_sends_idempotency_key_to_mercadopago(monkeypatch):
    captured = {}

    class FakeRequestOptions:
        def __init__(self, access_token=None, custom_headers=None):
            self.access_token = access_token
            self.custom_headers = custom_headers or {}

    class FakePreference:
        def create(self, preference_data, request_options=None):
            captured["preference_data"] = preference_data
            captured["headers"] = request_options.custom_headers
            return {
                "status": 201,
                "response": {
                    "id": "pref-test",
                    "init_point": "https://mp/init",
                    "sandbox_init_point": "https://mp/sandbox",
                },
            }

    class FakeSDK:
        def __init__(self, access_token):
            captured["access_token"] = access_token

        def preference(self):
            return FakePreference()

    fake_mp = types.SimpleNamespace(SDK=FakeSDK)
    fake_config = types.SimpleNamespace(RequestOptions=FakeRequestOptions)

    monkeypatch.setitem(sys.modules, "mercadopago", fake_mp)
    monkeypatch.setitem(sys.modules, "mercadopago.config", fake_config)
    monkeypatch.setenv("MP_ACCESS_TOKEN", "TEST-token")
    monkeypatch.setenv("NGROK_URL", "https://demo.ngrok-free.app")
    monkeypatch.setenv(
        "MP_WEBHOOK_URL",
        "https://demo.ngrok-free.app/api/v1/pagos/webhook",
    )
    get_settings.cache_clear()
    
    try:
        response = pago_service._crear_preferencia_mp(
            monto=1500.0,
            titulo="Pedido #1 - Food Store",
            pedido_id=1,
            back_urls={"success": "ok", "failure": "fail", "pending": "pending"},
            idempotency_key="idem-123",
        )
    finally:
        get_settings.cache_clear()

    assert response["preference_id"] == "pref-test"
    assert captured["headers"] == {"x-idempotency-key": "idem-123"}
    assert captured["preference_data"]["notification_url"] == "https://demo.ngrok-free.app/api/v1/pagos/webhook"
