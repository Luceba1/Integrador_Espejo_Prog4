from app.services import estadistica_service


def test_estadisticas_functional_uses_official_commercial_states():
    assert estadistica_service.ESTADOS_COMERCIALES == {"CONFIRMADO", "EN_PREP", "ENTREGADO"}
    assert "CANCELADO" not in estadistica_service.ESTADOS_COMERCIALES
    assert "EN_PREPARACION" not in estadistica_service.ESTADOS_COMERCIALES
