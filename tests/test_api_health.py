def test_health_endpoint(client):
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_health_ready_endpoint(client):
    """Health/ready should return 200 or 503 (degraded is acceptable if no DB/Redis)."""
    response = client.get("/api/v1/health/ready")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "checks" in data
    assert "database" in data["checks"]


def test_metrics_endpoint(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    # Should return prometheus text format or "not installed" message
    assert response.text is not None


def test_cors_restricted(client):
    """CORS should not allow arbitrary origins by default."""
    response = client.options("/api/v1/health/", headers={
        "Origin": "https://evil.com",
        "Access-Control-Request-Method": "GET",
    })
    acao = response.headers.get("access-control-allow-origin", "")
    assert "evil" not in acao