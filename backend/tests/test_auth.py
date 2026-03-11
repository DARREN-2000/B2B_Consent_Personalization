"""Tests for authentication endpoints."""


def test_register_and_login(client, org):
    # Register
    resp = client.post("/api/auth/register", json={
        "email": "newuser@testcorp.example",
        "name": "New User",
        "password": "SecurePass1!",
        "organization_id": org["id"],
    })
    assert resp.status_code == 201, resp.json
    assert resp.json["user"]["email"] == "newuser@testcorp.example"

    # Login
    resp = client.post("/api/auth/login", json={
        "email": "newuser@testcorp.example",
        "password": "SecurePass1!",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json
    assert "refresh_token" in resp.json


def test_login_wrong_password(client, admin_user):
    resp = client.post("/api/auth/login", json={
        "email": "admin@testcorp.example",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


def test_login_missing_fields(client):
    resp = client.post("/api/auth/login", json={"email": "a@b.com"})
    assert resp.status_code == 400


def test_me(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json["email"] == "admin@testcorp.example"


def test_me_no_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_refresh_token(client, admin_user):
    # Login to get refresh token
    login = client.post("/api/auth/login", json={
        "email": "admin@testcorp.example",
        "password": "TestPass123!",
    })
    refresh_token = login.json["refresh_token"]

    # Use refresh token
    resp = client.post(
        "/api/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json
