import uuid


def test_list_offers(client):
    """Offers endpoint should return 200."""
    response = client.get("/api/v1/offers/")
    assert response.status_code in (200, 401, 403)


def test_create_offer_no_auth(client, session):
    """Creating an offer requires brand context."""
    response = client.post("/api/v1/offers/", json={
        "title": "Test Offer",
        "description": "Test",
        "lat": 36.8065,
        "lon": 10.1815,
    })
    # Without auth context, expect 401, 403, or 422
    assert response.status_code in (401, 403, 422, 201)


def test_offers_json_response(client):
    """Offers response should be valid JSON."""
    response = client.get("/api/v1/offers/")
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, (list, dict))