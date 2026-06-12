from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.core import rate_limit
from app.core.auth_dependencies import _extraer_bearer_token
from app.core.security import (
    create_access_token,
    create_refresh_token_value,
    decode_access_token,
    hash_password,
    hash_refresh_token,
    refresh_token_expiration,
    verify_password,
)


class DummyRequest:
    def __init__(self, ip="127.0.0.1", forwarded=None):
        self.headers = {}
        if forwarded:
            self.headers["x-forwarded-for"] = forwarded
        self.client = SimpleNamespace(host=ip)


def test_hash_password_and_verify_password_roundtrip():
    hashed = hash_password("ClaveSegura123")
    assert hashed != "ClaveSegura123"
    assert verify_password("ClaveSegura123", hashed) is True
    assert verify_password("otra-clave", hashed) is False


def test_create_and_decode_access_token_contains_subject_roles_and_type():
    token = create_access_token("10", {"roles": ["ADMIN"]})
    payload = decode_access_token(token)
    assert payload["sub"] == "10"
    assert payload["roles"] == ["ADMIN"]
    assert payload["type"] == "access"
    assert "exp" in payload


def test_refresh_token_value_is_random_and_urlsafe():
    token_a = create_refresh_token_value()
    token_b = create_refresh_token_value()
    assert token_a != token_b
    assert len(token_a) > 40
    assert " " not in token_a


def test_hash_refresh_token_is_deterministic_sha256_hex():
    hashed_1 = hash_refresh_token("abc")
    hashed_2 = hash_refresh_token("abc")
    assert hashed_1 == hashed_2
    assert len(hashed_1) == 64
    assert hashed_1 != "abc"


def test_refresh_token_expiration_is_future_datetime():
    expires = refresh_token_expiration()
    assert expires > datetime.now(timezone.utc)
    assert expires.tzinfo is not None


def test_bearer_token_extraction_accepts_only_valid_scheme():
    assert _extraer_bearer_token("Bearer abc123") == "abc123"
    assert _extraer_bearer_token("bearer token") == "token"
    assert _extraer_bearer_token("Basic token") is None
    assert _extraer_bearer_token(None) is None


def test_auth_rate_limit_uses_forwarded_ip_and_raises_after_limit():
    request = DummyRequest(forwarded="10.0.0.1, 127.0.0.1")
    rate_limit.clear_failed_auth_attempts(request)
    for _ in range(5):
        rate_limit.register_failed_auth_attempt(request)
    with pytest.raises(HTTPException) as exc:
        rate_limit.check_auth_rate_limit(request)
    assert exc.value.status_code == 429
    assert "Retry-After" in exc.value.headers
    rate_limit.clear_failed_auth_attempts(request)
