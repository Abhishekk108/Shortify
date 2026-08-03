"""
Tests for:
  - verify_access_token() in app/utils/jwt.py
  - get_current_user() dependency behaviour
  - Protected URL endpoints (401 without token, 200/201 with valid token)
  - Protected analytics endpoints
  - GET /api/auth/me
"""
from datetime import timedelta

import pytest
from jose import JWTError

from app.utils.jwt import create_access_token, verify_access_token


# ── verify_access_token unit tests ────────────────────────────────────────────

class TestVerifyAccessToken:
    def test_returns_subject_for_valid_token(self):
        token = create_access_token({"sub": "user@example.com"})
        subject = verify_access_token(token)
        assert subject == "user@example.com"

    def test_raises_on_expired_token(self):
        token = create_access_token(
            {"sub": "user@example.com"},
            expires_delta=timedelta(seconds=-1),   # already expired
        )
        with pytest.raises(JWTError):
            verify_access_token(token)

    def test_raises_on_tampered_token(self):
        token = create_access_token({"sub": "user@example.com"})
        tampered = token[:-4] + "XXXX"
        with pytest.raises(JWTError):
            verify_access_token(tampered)

    def test_raises_on_missing_sub_claim(self):
        # Token with no "sub" claim
        token = create_access_token({"role": "admin"})   # no sub
        with pytest.raises(JWTError):
            verify_access_token(token)

    def test_raises_on_garbage_string(self):
        with pytest.raises(JWTError):
            verify_access_token("not.a.jwt")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _register_and_login(client, username="testuser", email="test@example.com",
                         password="securepass1"):
    """Register a user and return the access token."""
    client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": password,
    })
    r = client.post("/api/auth/login", json={
        "identifier": email,
        "password": password,
    })
    return r.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── GET /api/auth/me ──────────────────────────────────────────────────────────

class TestGetMe:
    def test_me_with_valid_token(self, client):
        token = _register_and_login(client)
        r = client.get("/api/auth/me", headers=_auth_headers(token))
        assert r.status_code == 200
        data = r.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert "hashed_password" not in data

    def test_me_without_token_returns_401(self, client):
        r = client.get("/api/auth/me")
        assert r.status_code == 401

    def test_me_with_invalid_token_returns_401(self, client):
        r = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.jwt.token"})
        assert r.status_code == 401

    def test_me_with_expired_token_returns_401(self, client):
        token = create_access_token(
            {"sub": "test@example.com"},
            expires_delta=timedelta(seconds=-1),
        )
        r = client.get("/api/auth/me", headers=_auth_headers(token))
        assert r.status_code == 401


# ── Protected URL endpoints ───────────────────────────────────────────────────

class TestProtectedUrlEndpoints:
    """All /api/urls endpoints must return 401 without a valid token."""

    def test_post_urls_requires_auth(self, client):
        r = client.post("/api/urls", json={"original_url": "https://example.com"})
        assert r.status_code == 401

    def test_get_urls_requires_auth(self, client):
        r = client.get("/api/urls")
        assert r.status_code == 401

    def test_get_url_by_id_requires_auth(self, client):
        r = client.get("/api/urls/1")
        assert r.status_code == 401

    def test_delete_url_requires_auth(self, client):
        r = client.delete("/api/urls/1")
        assert r.status_code == 401

    def test_post_urls_with_token_succeeds(self, client):
        token = _register_and_login(client)
        r = client.post(
            "/api/urls",
            json={"original_url": "https://example.com/protected"},
            headers=_auth_headers(token),
        )
        assert r.status_code == 201
        assert "short_code" in r.json()

    def test_get_urls_with_token_succeeds(self, client):
        token = _register_and_login(client)
        r = client.get("/api/urls", headers=_auth_headers(token))
        assert r.status_code == 200
        assert "items" in r.json()

    def test_get_url_by_id_with_token_succeeds(self, client):
        token = _register_and_login(client)
        created = client.post(
            "/api/urls",
            json={"original_url": "https://example.com/get-by-id"},
            headers=_auth_headers(token),
        )
        url_id = created.json()["id"]
        r = client.get(f"/api/urls/{url_id}", headers=_auth_headers(token))
        assert r.status_code == 200
        assert r.json()["id"] == url_id

    def test_delete_url_with_token_succeeds(self, client):
        token = _register_and_login(client)
        created = client.post(
            "/api/urls",
            json={"original_url": "https://example.com/to-delete"},
            headers=_auth_headers(token),
        )
        url_id = created.json()["id"]
        r = client.delete(f"/api/urls/{url_id}", headers=_auth_headers(token))
        assert r.status_code == 204

    def test_invalid_token_on_protected_endpoint_returns_401(self, client):
        r = client.get("/api/urls", headers={"Authorization": "Bearer bad.token.here"})
        assert r.status_code == 401


# ── Protected analytics endpoints ────────────────────────────────────────────

class TestProtectedAnalyticsEndpoints:
    def test_summary_requires_auth(self, client):
        r = client.get("/api/analytics/summary")
        assert r.status_code == 401

    def test_url_analytics_requires_auth(self, client):
        r = client.get("/api/urls/1/analytics")
        assert r.status_code == 401

    def test_summary_with_token_succeeds(self, client):
        token = _register_and_login(client)
        r = client.get("/api/analytics/summary", headers=_auth_headers(token))
        assert r.status_code == 200
        data = r.json()
        assert "total_links" in data
        assert "total_clicks" in data
        assert "top_urls" in data

    def test_url_analytics_with_token_succeeds(self, client):
        token = _register_and_login(client)
        created = client.post(
            "/api/urls",
            json={"original_url": "https://example.com/analytics-test"},
            headers=_auth_headers(token),
        )
        url_id = created.json()["id"]
        r = client.get(f"/api/urls/{url_id}/analytics", headers=_auth_headers(token))
        assert r.status_code == 200
        assert r.json()["url_id"] == url_id

    def test_url_analytics_404_with_token(self, client):
        token = _register_and_login(client)
        r = client.get("/api/urls/99999/analytics", headers=_auth_headers(token))
        assert r.status_code == 404


# ── Public endpoints must still work ─────────────────────────────────────────

class TestPublicEndpointsUnaffected:
    """Redirect and health endpoints must remain public (no auth required)."""

    def test_health_is_public(self, client):
        r = client.get("/health")
        assert r.status_code == 200

    def test_redirect_is_public(self, client):
        """Create a URL with auth, then visit the short code without auth."""
        token = _register_and_login(client)
        created = client.post(
            "/api/urls",
            json={"original_url": "https://example.com/redirect-test"},
            headers=_auth_headers(token),
        )
        code = created.json()["short_code"]
        r = client.get(f"/{code}", follow_redirects=False)
        # 307 redirect — no token needed
        assert r.status_code == 307
