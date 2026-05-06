from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_redis, rate_limit
from app.models import Link, Click
from app.services.geolocation import get_country

router = APIRouter(tags=["redirect"])


@router.get("/{code}")
async def redirect_to_url(
    code: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    client_ip = request.headers.get("X-Forwarded-For", request.client.host).split(",")[0].strip()
    await rate_limit(f"redirect:{client_ip}", limit=60, window=60, redis=redis)

    result = await db.execute(select(Link).where(Link.code == code, Link.is_active == True))
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    if link.expires_at:
        expires = link.expires_at.replace(tzinfo=timezone.utc) if link.expires_at.tzinfo is None else link.expires_at
        if expires < datetime.now(timezone.utc):
            raise HTTPException(status_code=410, detail="This link has expired")
    country = await get_country(client_ip)

    click = Click(
        link_id=link.id,
        country=country,
        referrer=request.headers.get("referer"),
        user_agent=request.headers.get("user-agent"),
        ip_address=client_ip,
    )
    link.click_count += 1
    db.add(click)
    await db.commit()

    return RedirectResponse(url=link.original_url, status_code=302)
