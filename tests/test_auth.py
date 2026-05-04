import pytest


@pytest.mark.asyncio
async def test_register(client):
    resp = await client.post("/auth/register", json={"email": "a@b.com", "password": "pass123"})
    assert resp.status_code == 201
    assert resp.json()["email"] == "a@b.com"


@pytest.mark.asyncio
async def test_duplicate_register(client):
    await client.post("/auth/register", json={"email": "a@b.com", "password": "pass123"})
    resp = await client.post("/auth/register", json={"email": "a@b.com", "password": "pass123"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_login(client):
    await client.post("/auth/register", json={"email": "a@b.com", "password": "pass123"})
    resp = await client.post("/auth/login", json={"email": "a@b.com", "password": "pass123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_wrong_password(client):
    await client.post("/auth/register", json={"email": "a@b.com", "password": "pass123"})
    resp = await client.post("/auth/login", json={"email": "a@b.com", "password": "wrong"})
    assert resp.status_code == 401
