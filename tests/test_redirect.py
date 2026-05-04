import pytest


@pytest.mark.asyncio
async def test_redirect(auth_client, client):
    resp = await auth_client.post("/links/", json={"original_url": "https://example.com"})
    code = resp.json()["code"]
    red = await client.get(f"/{code}", follow_redirects=False)
    assert red.status_code == 302
    assert red.headers["location"] == "https://example.com/"


@pytest.mark.asyncio
async def test_redirect_not_found(client):
    resp = await client.get("/nonexistent", follow_redirects=False)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_click_count_increments(auth_client, client):
    resp = await auth_client.post("/links/", json={"original_url": "https://example.com"})
    code = resp.json()["code"]
    await client.get(f"/{code}", follow_redirects=False)
    await client.get(f"/{code}", follow_redirects=False)
    links = await auth_client.get("/links/")
    assert links.json()[0]["click_count"] == 2
