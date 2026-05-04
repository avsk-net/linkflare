import pytest


@pytest.mark.asyncio
async def test_create_link(auth_client):
    resp = await auth_client.post("/links/", json={"original_url": "https://example.com"})
    assert resp.status_code == 201
    data = resp.json()
    assert "code" in data
    assert data["click_count"] == 0


@pytest.mark.asyncio
async def test_list_links(auth_client):
    await auth_client.post("/links/", json={"original_url": "https://example.com"})
    resp = await auth_client.get("/links/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_custom_code(auth_client):
    resp = await auth_client.post("/links/", json={"original_url": "https://example.com", "custom_code": "mycode"})
    assert resp.status_code == 201
    assert resp.json()["code"] == "mycode"


@pytest.mark.asyncio
async def test_delete_link(auth_client):
    resp = await auth_client.post("/links/", json={"original_url": "https://example.com"})
    code = resp.json()["code"]
    del_resp = await auth_client.delete(f"/links/{code}")
    assert del_resp.status_code == 204
