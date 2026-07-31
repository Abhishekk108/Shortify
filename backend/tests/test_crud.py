"""
Unit tests for app/crud/url.py
"""
from datetime import datetime, timedelta

import pytest

from app.crud.url import (
    create_click,
    create_url,
    delete_url,
    get_url_by_code,
    get_url_by_id,
    increment_click_count,
    list_urls,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_url(db, *, original_url="https://example.com", short_code="abc123",
             custom_alias=None, expires_at=None):
    return create_url(
        db,
        original_url=original_url,
        short_code=short_code,
        custom_alias=custom_alias,
        expires_at=expires_at,
    )


# ── create_url ────────────────────────────────────────────────────────────────

class TestCreateUrl:
    def test_creates_and_returns_url(self, db):
        url = make_url(db)
        assert url.id is not None
        assert url.original_url == "https://example.com"
        assert url.short_code == "abc123"

    def test_defaults(self, db):
        url = make_url(db)
        assert url.is_active is True
        assert url.click_count == 0
        assert url.custom_alias is None
        assert url.expires_at is None

    def test_with_custom_alias(self, db):
        url = make_url(db, short_code="xalias", custom_alias="my-link")
        assert url.custom_alias == "my-link"

    def test_with_expiry(self, db):
        exp = datetime.utcnow() + timedelta(days=7)
        url = make_url(db, short_code="xexp", expires_at=exp)
        assert url.expires_at is not None


# ── get_url_by_code ───────────────────────────────────────────────────────────

class TestGetUrlByCode:
    def test_finds_by_short_code(self, db):
        make_url(db, short_code="find01")
        found = get_url_by_code(db, "find01")
        assert found is not None
        assert found.short_code == "find01"

    def test_finds_by_custom_alias(self, db):
        make_url(db, short_code="find02", custom_alias="alias-find")
        found = get_url_by_code(db, "alias-find")
        assert found is not None
        assert found.custom_alias == "alias-find"

    def test_returns_none_for_unknown_code(self, db):
        result = get_url_by_code(db, "no-such-code")
        assert result is None

    def test_short_code_takes_priority_over_alias(self, db):
        """If short_code matches, return that record — not another record's alias."""
        url1 = make_url(db, short_code="priority", custom_alias=None)
        url2 = make_url(db, short_code="other999", custom_alias="priority-alias")

        result = get_url_by_code(db, "priority")
        assert result.id == url1.id


# ── get_url_by_id ─────────────────────────────────────────────────────────────

class TestGetUrlById:
    def test_finds_existing_url(self, db):
        url = make_url(db, short_code="byid01")
        found = get_url_by_id(db, url.id)
        assert found is not None
        assert found.id == url.id

    def test_returns_none_for_missing_id(self, db):
        assert get_url_by_id(db, 99999) is None


# ── list_urls ─────────────────────────────────────────────────────────────────

class TestListUrls:
    def _seed(self, db):
        make_url(db, original_url="https://google.com", short_code="list01")
        make_url(db, original_url="https://github.com", short_code="list02")
        make_url(db, original_url="https://fastapi.tiangolo.com", short_code="list03",
                 custom_alias="fapi")

    def test_returns_all_urls(self, db):
        self._seed(db)
        results = list_urls(db)
        assert len(results) == 3

    def test_search_by_original_url(self, db):
        self._seed(db)
        results = list_urls(db, search="github")
        assert len(results) == 1
        assert "github.com" in results[0].original_url

    def test_search_by_short_code(self, db):
        self._seed(db)
        results = list_urls(db, search="list02")
        assert len(results) == 1
        assert results[0].short_code == "list02"

    def test_search_by_custom_alias(self, db):
        self._seed(db)
        results = list_urls(db, search="fapi")
        assert len(results) == 1
        assert results[0].custom_alias == "fapi"

    def test_search_is_case_insensitive(self, db):
        self._seed(db)
        results = list_urls(db, search="GITHUB")
        assert len(results) == 1

    def test_search_no_match_returns_empty(self, db):
        self._seed(db)
        results = list_urls(db, search="zzz-no-match")
        assert results == []

    def test_pagination_skip(self, db):
        self._seed(db)
        results = list_urls(db, skip=1, limit=10)
        assert len(results) == 2

    def test_pagination_limit(self, db):
        self._seed(db)
        results = list_urls(db, skip=0, limit=2)
        assert len(results) == 2

    def test_ordered_newest_first(self, db):
        self._seed(db)
        results = list_urls(db)
        dates = [r.created_at for r in results]
        assert dates == sorted(dates, reverse=True)


# ── delete_url ────────────────────────────────────────────────────────────────

class TestDeleteUrl:
    def test_deletes_existing_url(self, db):
        url = make_url(db, short_code="del01")
        result = delete_url(db, url.id)
        assert result is True
        assert get_url_by_id(db, url.id) is None

    def test_returns_false_for_missing_url(self, db):
        result = delete_url(db, 99999)
        assert result is False

    def test_cascade_deletes_clicks(self, db):
        url = make_url(db, short_code="del02")
        create_click(db, url_id=url.id, ip_address="1.2.3.4",
                     user_agent="pytest", referrer=None)
        delete_url(db, url.id)
        # After cascade delete, no clicks should exist for that url_id
        from app.models.click import Click
        remaining = db.query(Click).filter(Click.url_id == url.id).all()
        assert remaining == []


# ── increment_click_count ─────────────────────────────────────────────────────

class TestIncrementClickCount:
    def test_increments_by_one(self, db):
        url = make_url(db, short_code="inc01")
        assert url.click_count == 0
        increment_click_count(db, url.id)
        db.refresh(url)
        assert url.click_count == 1

    def test_multiple_increments(self, db):
        url = make_url(db, short_code="inc02")
        for _ in range(5):
            increment_click_count(db, url.id)
        db.refresh(url)
        assert url.click_count == 5


# ── create_click ─────────────────────────────────────────────────────────────

class TestCreateClick:
    def test_creates_click_record(self, db):
        url = make_url(db, short_code="clk01")
        click = create_click(
            db, url_id=url.id,
            ip_address="203.0.113.1",
            user_agent="Mozilla/5.0",
            referrer="https://google.com",
        )
        assert click.id is not None
        assert click.url_id == url.id
        assert click.ip_address == "203.0.113.1"

    def test_nullable_fields_accepted(self, db):
        url = make_url(db, short_code="clk02")
        click = create_click(db, url_id=url.id,
                              ip_address=None, user_agent=None, referrer=None)
        assert click.id is not None
        assert click.ip_address is None
