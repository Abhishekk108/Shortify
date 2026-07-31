"""
Unit tests for app/services/validator.py
"""
import pytest

from app.services.validator import validate_url, is_safe_url


# ── validate_url ──────────────────────────────────────────────────────────────

class TestValidateUrl:

    # ── valid inputs ──────────────────────────────────────────────────────────
    def test_valid_https_url(self):
        result = validate_url("https://example.com/path?q=1")
        assert result == "https://example.com/path?q=1"

    def test_valid_http_url(self):
        result = validate_url("http://example.com")
        assert result == "http://example.com"

    def test_strips_leading_whitespace(self):
        result = validate_url("   https://example.com")
        assert result == "https://example.com"

    def test_strips_trailing_whitespace(self):
        result = validate_url("https://example.com   ")
        assert result == "https://example.com"

    def test_strips_both_sides(self):
        result = validate_url("  https://example.com  ")
        assert result == "https://example.com"

    def test_url_with_port(self):
        result = validate_url("http://localhost:8000/api")
        assert "localhost" in result

    def test_url_with_path_and_query(self):
        result = validate_url("https://docs.python.org/3/library/urllib.html?highlight=parse")
        assert result.startswith("https://")

    # ── invalid inputs ────────────────────────────────────────────────────────
    def test_rejects_empty_string(self):
        with pytest.raises(ValueError, match="empty"):
            validate_url("")

    def test_rejects_whitespace_only(self):
        with pytest.raises(ValueError, match="empty"):
            validate_url("   ")

    def test_rejects_javascript_scheme(self):
        with pytest.raises(ValueError, match="javascript"):
            validate_url("javascript:alert(1)")

    def test_rejects_ftp_scheme(self):
        with pytest.raises(ValueError, match="ftp"):
            validate_url("ftp://files.example.com")

    def test_rejects_file_scheme(self):
        with pytest.raises(ValueError, match="file"):
            validate_url("file:///etc/passwd")

    def test_rejects_data_scheme(self):
        with pytest.raises(ValueError):
            validate_url("data:text/html,<h1>test</h1>")

    def test_rejects_no_scheme(self):
        with pytest.raises(ValueError):
            validate_url("example.com/path")

    def test_rejects_missing_host(self):
        with pytest.raises(ValueError, match="host"):
            validate_url("https://")

    def test_rejects_only_scheme(self):
        with pytest.raises(ValueError):
            validate_url("https:")


# ── is_safe_url ───────────────────────────────────────────────────────────────

class TestIsSafeUrl:
    def test_public_domain_is_safe(self):
        # example.com resolves to a public IP
        assert is_safe_url("https://example.com") is True

    def test_localhost_is_not_safe(self):
        assert is_safe_url("http://localhost/admin") is False

    def test_127_loopback_is_not_safe(self):
        assert is_safe_url("http://127.0.0.1/secret") is False

    def test_ipv6_loopback_is_not_safe(self):
        assert is_safe_url("http://[::1]/secret") is False

    def test_private_10_range_is_not_safe(self):
        assert is_safe_url("http://10.0.0.1/internal") is False

    def test_private_192_168_range_is_not_safe(self):
        assert is_safe_url("http://192.168.1.1/router") is False

    def test_private_172_16_range_is_not_safe(self):
        assert is_safe_url("http://172.16.0.1/internal") is False

    def test_unresolvable_host_fails_open(self):
        # An unresolvable hostname should return True (fail open)
        result = is_safe_url("https://this-host-definitely-does-not-exist-xyz123.invalid")
        assert result is True
