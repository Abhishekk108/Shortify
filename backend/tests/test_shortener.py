"""
Unit tests for app/services/shortener.py
"""
import string
from unittest.mock import MagicMock, patch

import pytest

from app.services.shortener import BASE62_CHARS, generate_short_code, get_unique_short_code

BASE62 = set(string.ascii_letters + string.digits)


# ── generate_short_code ───────────────────────────────────────────────────────

class TestGenerateShortCode:
    def test_default_length_is_six(self):
        code = generate_short_code()
        assert len(code) == 6

    def test_custom_length(self):
        for length in [4, 8, 12]:
            code = generate_short_code(length=length)
            assert len(code) == length, f"Expected {length}, got {len(code)}"

    def test_only_base62_characters(self):
        for _ in range(100):
            code = generate_short_code()
            assert all(c in BASE62 for c in code), f"Non-base62 char in: {code}"

    def test_uniqueness(self):
        """1 000 codes should almost certainly all be distinct (collision probability ~0)."""
        codes = {generate_short_code() for _ in range(1_000)}
        # Allow at most 1 collision out of 1 000 (extremely conservative)
        assert len(codes) >= 999

    def test_zero_length_returns_empty_string(self):
        assert generate_short_code(length=0) == ""

    def test_length_one(self):
        code = generate_short_code(length=1)
        assert len(code) == 1
        assert code in BASE62


# ── get_unique_short_code ─────────────────────────────────────────────────────

class TestGetUniqueShortCode:
    def test_returns_code_when_no_collision(self, db):
        code = get_unique_short_code(db)
        assert len(code) == 6
        assert all(c in BASE62 for c in code)

    def test_skips_colliding_codes(self, db):
        """Patch generate_short_code so the first 3 calls return the same code,
        then return a unique one — verifies the retry loop."""
        from app.crud.url import create_url

        # Pre-insert a URL with code "AAAA11"
        existing_code = "AAAA11"
        create_url(db, original_url="https://example.com", short_code=existing_code)

        call_count = {"n": 0}

        def _patched_generate(length=6):
            call_count["n"] += 1
            if call_count["n"] <= 3:
                return existing_code      # always collide first 3 times
            return "ZZZZZZ"              # unique on 4th attempt

        with patch("app.services.shortener.generate_short_code", side_effect=_patched_generate):
            result = get_unique_short_code(db)

        assert result == "ZZZZZZ"
        assert call_count["n"] == 4

    def test_raises_after_ten_collisions(self, db):
        """If every generated code collides, RuntimeError must be raised."""
        with patch(
            "app.services.shortener.generate_short_code",
            return_value="FIXED1",   # always returns same code
        ):
            from app.crud.url import create_url
            create_url(db, original_url="https://example.com", short_code="FIXED1")

            with pytest.raises(RuntimeError, match="Unable to generate"):
                get_unique_short_code(db)
