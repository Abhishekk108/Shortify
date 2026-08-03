"""
Integration tests for the FastAPI endpoints.
Uses TestClient with an in-memory SQLite DB (see conftest.py).

All protected endpoints use the `auth_client` fixture which automatically
attaches a valid Bearer token to every request.
"""
from datetime import datetime, timedelta
from app.crud.url import create_url


# ── /health (public — uses plain client) ──────────────────────────────────────

class TestHealth:
    def test_health_check(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


# ── POST /api/urls ────────────────────────────────────────────────────────────

class TestCreateUrl:
    def test_creates_short_url(self, auth_client):
        r = auth_client.post("/api/urls", json={"original_url": "https://example.com"})
        assert r.status_code == 201
        data = r.json()
        assert "example.com" in data["original_url"]
        assert "short_code" in data
        assert "short_url" in data
        assert data["click_count"] == 0

    def test_creates_with_custom_alias(self, auth_client):
        r = auth_client.post("/api/urls", json={
            "original_url": "https://example.com",
            "custom_alias": "my-alias",
        })
        assert r.status_code == 201
        assert r.json()["short_code"] == "my-alias"

    def test_rejects_invalid_url_scheme(self, auth_client):
        r = auth_client.post("/api/urls", json={"original_url": "ftp://example.com"})
        assert r.status_code in (400, 422)

    def test_rejects_missing_url(self, auth_client):
        r = auth_client.post("/api/urls", json={})
        assert r.status_code == 422

    def test_rejects_duplicate_alias(self, auth_client):
        auth_client.post("/api/urls", json={
            "original_url": "https://example.com",
            "custom_alias": "dup-alias",
        })
        r = auth_client.post("/api/urls", json={
            "original_url": "https://other.com",
            "custom_alias": "dup-alias",
        })
        assert r.status_code == 409

    def test_rejects_alias_too_short(self, auth_client):
        r = auth_client.post("/api/urls", json={
            "original_url": "https://example.com",
            "custom_alias": "ab",
        })
        assert r.status_code == 422

    def test_rejects_alias_with_spaces(self, auth_client):
        r = auth_client.post("/api/urls", json={
            "original_url": "https://example.com",
            "custom_alias": "bad alias",
        })
        assert r.status_code == 422


# ── GET /api/urls ─────────────────────────────────────────────────────────────

class TestListUrls:
    def test_returns_empty_list(self, auth_client):
        r = auth_client.get("/api/urls")
        assert r.status_code == 200
        data = r.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_returns_created_url(self, auth_client):
        auth_client.post("/api/urls", json={"original_url": "https://list-test.com"})
        r = auth_client.get("/api/urls")
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_search_filter(self, auth_client):
        auth_client.post("/api/urls", json={
            "original_url": "https://searchable-unique-xyz.com",
        })
        r = auth_client.get("/api/urls", params={"search": "searchable-unique-xyz"})
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_pagination(self, auth_client):
        for i in range(5):
            auth_client.post("/api/urls", json={"original_url": f"https://page-test-{i}.com"})
        r = auth_client.get("/api/urls", params={"skip": 0, "limit": 2})
        assert r.status_code == 200
        assert len(r.json()["items"]) <= 2


# ── GET /api/urls/{id} ────────────────────────────────────────────────────────

class TestGetUrl:
    def test_get_existing_url(self, auth_client):
        created = auth_client.post("/api/urls", json={"original_url": "https://get-me.com"})
        url_id = created.json()["id"]
        r = auth_client.get(f"/api/urls/{url_id}")
        assert r.status_code == 200
        assert r.json()["id"] == url_id

    def test_returns_404_for_missing(self, auth_client):
        r = auth_client.get("/api/urls/99999")
        assert r.status_code == 404


# ── DELETE /api/urls/{id} ─────────────────────────────────────────────────────

class TestDeleteUrl:
    def test_deletes_url(self, auth_client):
        created = auth_client.post("/api/urls", json={"original_url": "https://delete-me.com"})
        url_id = created.json()["id"]
        r = auth_client.delete(f"/api/urls/{url_id}")
        assert r.status_code == 204
        assert auth_client.get(f"/api/urls/{url_id}").status_code == 404

    def test_returns_404_for_missing(self, auth_client):
        r = auth_client.delete("/api/urls/99999")
        assert r.status_code == 404


# ── GET /{short_code} — redirect (public) ─────────────────────────────────────

class TestRedirect:
    def test_redirects_to_original_url(self, auth_client):
        created = auth_client.post("/api/urls", json={"original_url": "https://redirect-target.com"})
        code = created.json()["short_code"]
        r = auth_client.get(f"/{code}", follow_redirects=False)
        assert r.status_code == 307
        assert "redirect-target.com" in r.headers["location"]

    def test_increments_click_count(self, auth_client):
        created = auth_client.post("/api/urls", json={"original_url": "https://click-count.com"})
        data = created.json()
        code = data["short_code"]
        url_id = data["id"]
        auth_client.get(f"/{code}", follow_redirects=False)
        auth_client.get(f"/{code}", follow_redirects=False)
        r = auth_client.get(f"/api/urls/{url_id}")
        assert r.json()["click_count"] == 2

    def test_returns_404_for_unknown_code(self, client):
        r = client.get("/no-such-code-xyz", follow_redirects=False)
        assert r.status_code == 404

    def test_returns_410_for_inactive_link(self, client, db):
        url = create_url(db, original_url="https://inactive.com",
                         short_code="inactive1")
        url.is_active = False
        db.commit()
        r = client.get("/inactive1", follow_redirects=False)
        assert r.status_code == 410

    def test_returns_410_for_expired_link(self, client, db):
        past = datetime.utcnow() - timedelta(days=1)
        create_url(db, original_url="https://expired.com",
                   short_code="expired1", expires_at=past)
        r = client.get("/expired1", follow_redirects=False)
        assert r.status_code == 410

    def test_redirects_by_custom_alias(self, auth_client):
        auth_client.post("/api/urls", json={
            "original_url": "https://alias-target.com",
            "custom_alias": "my-redir",
        })
        r = auth_client.get("/my-redir", follow_redirects=False)
        assert r.status_code == 307
        assert "alias-target.com" in r.headers["location"]


# ── GET /api/analytics/summary ────────────────────────────────────────────────

class TestAnalyticsSummary:
    def test_summary_returns_correct_shape(self, auth_client):
        r = auth_client.get("/api/analytics/summary")
        assert r.status_code == 200
        data = r.json()
        assert "total_links" in data
        assert "total_clicks" in data
        assert "top_urls" in data
        assert isinstance(data["top_urls"], list)

    def test_summary_counts_links(self, auth_client):
        before = auth_client.get("/api/analytics/summary").json()["total_links"]
        auth_client.post("/api/urls", json={"original_url": "https://summary-test.com"})
        after = auth_client.get("/api/analytics/summary").json()["total_links"]
        assert after == before + 1


# ── GET /api/urls/{id}/analytics ─────────────────────────────────────────────

class TestUrlAnalytics:
    def test_analytics_empty_on_new_url(self, auth_client):
        created = auth_client.post("/api/urls", json={"original_url": "https://analytics-test.com"})
        url_id = created.json()["id"]
        r = auth_client.get(f"/api/urls/{url_id}/analytics")
        assert r.status_code == 200
        data = r.json()
        assert data["total_clicks"] == 0
        assert data["clicks"] == []

    def test_analytics_records_click(self, auth_client):
        created = auth_client.post("/api/urls", json={"original_url": "https://analytics-click.com"})
        code = created.json()["short_code"]
        url_id = created.json()["id"]
        auth_client.get(f"/{code}", follow_redirects=False)
        r = auth_client.get(f"/api/urls/{url_id}/analytics")
        assert r.status_code == 200
        assert len(r.json()["clicks"]) == 1

    def test_analytics_404_for_missing_url(self, auth_client):
        r = auth_client.get("/api/urls/99999/analytics")
        assert r.status_code == 404
