from fastapi.testclient import TestClient
from app.core.config import get_settings
from app.main import app

def test_password_gate_disabled_by_default():
    client = TestClient(app)
    # Retrieve settings and ensure site_access_password is None/empty by default in test config
    settings = get_settings()
    settings.site_access_password = None

    # Request health endpoint without header (both prefixed and root)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_password_gate_enabled():
    client = TestClient(app)
    settings = get_settings()
    settings.site_access_password = "test-secret-password"

    try:
        # Request health endpoint without header
        response = client.get("/api/v1/health")
        assert response.status_code == 401
        assert "Unauthorized" in response.json()["detail"]

        response = client.get("/health")
        assert response.status_code == 401
        assert "Unauthorized" in response.json()["detail"]

        # Request health endpoint with wrong header
        response = client.get("/api/v1/health", headers={"X-Site-Access-Password": "wrong-password"})
        assert response.status_code == 401

        response = client.get("/health", headers={"X-Site-Access-Password": "wrong-password"})
        assert response.status_code == 401

        # Request health endpoint with correct header
        response = client.get("/api/v1/health", headers={"X-Site-Access-Password": "test-secret-password"})
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

        response = client.get("/health", headers={"X-Site-Access-Password": "test-secret-password"})
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

        # Request docs endpoint (should bypass check even without password header)
        response = client.get("/docs")
        assert response.status_code == 200

        # Request openapi.json (should bypass check)
        response = client.get("/openapi.json")
        assert response.status_code == 200
    finally:
        # Restore settings
        settings.site_access_password = None

