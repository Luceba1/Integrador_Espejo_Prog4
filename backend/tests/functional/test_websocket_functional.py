from app.core.websocket import ConnectionManager


def test_websocket_functional_normalizes_order_payload_contract():
    manager = ConnectionManager()
    payload = manager._build_order_payload(
        "ORDER_STATE_CHANGED",
        {
            "pedido_id": 7,
            "usuario_id": 2,
            "old_state": "CONFIRMADO",
            "new_state": "EN_PREP",
            "changed_by": 1,
            "motivo": "Pedido enviado a cocina.",
        },
    )

    assert payload["event"] == "estado_cambiado"
    assert payload["pedido_id"] == 7
    assert payload["estado_anterior"] == "CONFIRMADO"
    assert payload["estado_nuevo"] == "EN_PREP"
    assert payload["motivo"] == "Pedido enviado a cocina."
    assert payload["timestamp"].endswith("Z")
