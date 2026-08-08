"""
Integration tests for POST /api/auth/register and POST /api/auth/login.
Uses the shared conftest.py fixtures (PostgreSQL-backed per-test rollback).
"""
import pytest


class TestRegister:
    def test_register_success(self, client):
        r = client.post("/api/auth/register", json={
            "username": "alice01",
            "email": "alice@example.com",
            "password": "securepass1",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["username"] == "alice01"
        assert data["email"] == "alice@example.com"
        assert "id" in data
        assert "created_at" in data

    def test_register_does_not_expose_password(self, client):
        r = client.post("/api/auth/register", json={
            "username": "bob01",
            "email": "bob@example.com",
            "password": "securepass1",
        })
        assert r.status_code == 201
        assert "hashed_password" not in r.json()
        assert "password" not in r.json()

    def test_register_duplicate_email(self, client):
        client.post("/api/auth/register", json={
            "username": "user1",
            "email": "dup@example.com",
            "password": "securepass1",
        })
        r = client.post("/api/auth/register", json={
            "username": "user2",
            "email": "dup@example.com",   # same email
            "password": "securepass1",
        })
        assert r.status_code == 409
        assert "email" in r.json()["detail"].lower()

    def test_register_duplicate_username(self, client):
        client.post("/api/auth/register", json={
            "username": "samename",
            "email": "first@example.com",
            "password": "securepass1",
        })
        r = client.post("/api/auth/register", json={
            "username": "samename",        # same username
            "email": "second@example.com",
            "password": "securepass1",
        })
        assert r.status_code == 409
        assert "username" in r.json()["detail"].lower()

    def test_register_short_password_rejected(self, client):
        r = client.post("/api/auth/register", json={
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "short",           # < 8 chars
        })
        assert r.status_code == 422

    def test_register_invalid_email_rejected(self, client):
        r = client.post("/api/auth/register", json={
            "username": "dave",
            "email": "not-an-email",
            "password": "securepass1",
        })
        assert r.status_code == 422

    def test_register_short_username_rejected(self, client):
        r = client.post("/api/auth/register", json={
            "username": "ab",              # < 3 chars
            "email": "short@example.com",
            "password": "securepass1",
        })
        assert r.status_code == 422

    def test_register_username_with_spaces_rejected(self, client):
        r = client.post("/api/auth/register", json={
            "username": "bad name",        # spaces not allowed
            "email": "space@example.com",
            "password": "securepass1",
        })
        assert r.status_code == 422


class TestLogin:
    def _register(self, client):
        """Helper — register a test user and return the response."""
        return client.post("/api/auth/register", json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "securepass1",
        })

    def test_login_by_email_returns_token(self, client):
        self._register(client)
        r = client.post("/api/auth/login", json={
            "identifier": "login@example.com",
            "password": "securepass1",
        })
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 20   # a real JWT is long

    def test_login_by_username_returns_token(self, client):
        self._register(client)
        r = client.post("/api/auth/login", json={
            "identifier": "loginuser",     # username
            "password": "securepass1",
        })
        assert r.status_code == 200
        assert "access_token" in r.json()

    def test_login_wrong_password_returns_401(self, client):
        self._register(client)
        r = client.post("/api/auth/login", json={
            "identifier": "login@example.com",
            "password": "wrongpassword!",
        })
        assert r.status_code == 401

    def test_login_unknown_user_returns_401(self, client):
        r = client.post("/api/auth/login", json={
            "identifier": "nobody@example.com",
            "password": "anypassword",
        })
        assert r.status_code == 401

    def test_login_no_user_enumeration(self, client):
        """Wrong password and unknown user must return identical error messages."""
        self._register(client)
        r_bad_pw = client.post("/api/auth/login", json={
            "identifier": "login@example.com",
            "password": "wrongpassword!",
        })
        r_no_user = client.post("/api/auth/login", json={
            "identifier": "nobody@example.com",
            "password": "anypassword",
        })
        assert r_bad_pw.json()["detail"] == r_no_user.json()["detail"]

    def test_login_missing_identifier_returns_422(self, client):
        r = client.post("/api/auth/login", json={"password": "securepass1"})
        assert r.status_code == 422

    def test_login_missing_password_returns_422(self, client):
        r = client.post("/api/auth/login", json={"identifier": "login@example.com"})
        assert r.status_code == 422
