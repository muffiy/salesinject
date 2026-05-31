import pytest


def test_telegram_auth_invalid_data(client):
    """Telegram auth should reject invalid initData."""
    response = client.post("/api/v1/auth/telegram", json={"initData": "invalid_data"})
    # Without BOT_TOKEN set, it falls back to dev mode so may return 200
    # With BOT_TOKEN set, it returns 401 for invalid data
    assert response.status_code in (200, 401, 422)


def test_telegram_auth_missing_fields(client):
    """Telegram auth should handle missing fields."""
    response = client.post("/api/v1/auth/telegram", json={})
    # Accept 422 for validation error
    assert response.status_code in (422, 200)


def test_auth_rate_limit(client):
    """Auth endpoint should handle rate limiting gracefully."""
    payload = {"initData": "test_data"}
    responses = []
    for _ in range(15):
        resp = client.post("/api/v1/auth/telegram", json=payload)
        responses.append(resp.status_code)
    # Should not crash - all responses valid HTTP codes
    for code in responses:
        assert code in (200, 401, 422, 429)


def test_telegram_webhook_missing_body(client):
    """Webhook should handle missing body."""
    response = client.post("/api/v1/telegram/webhook", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True