import httpx


async def get_country(ip: str) -> str | None:
    if ip in ("127.0.0.1", "::1", "testclient"):
        return "Local"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"http://ip-api.com/json/{ip}?fields=country")
            if resp.status_code == 200:
                data = resp.json()
                return data.get("country")
    except Exception:
        return None
    return None
