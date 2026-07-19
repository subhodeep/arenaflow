from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_includes_security_headers():
    client = TestClient(app)
    response = client.get("/healthz", headers={"X-Request-ID": "test-request"})

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["X-Request-ID"] == "test-request"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_validation_errors_use_consistent_error_shape():
    client = TestClient(app)
    response = client.post("/api/v1/assistant/chat", json={"venue_id": "", "message": "hello"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.json()["error"]["request_id"]
