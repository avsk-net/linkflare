from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Link, User
from app.schemas import AnalyticsSummary, ClickOut

router = APIRouter(prefix="/analytics", tags=["analytics"])
templates = Jinja2Templates(directory="app/templates")


async def _get_owned_link(code: str, user: User, db: AsyncSession) -> Link:
    result = await db.execute(
        select(Link)
        .options(selectinload(Link.clicks))
        .where(Link.code == code, Link.owner_id == user.id)
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


@router.get("/{code}/json", response_model=AnalyticsSummary)
async def get_analytics_json(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    link = await _get_owned_link(code, current_user, db)
    clicks_by_country = Counter(c.country or "Unknown" for c in link.clicks)
    recent = sorted(link.clicks, key=lambda c: c.clicked_at, reverse=True)[:20]
    return AnalyticsSummary(
        code=link.code,
        original_url=link.original_url,
        total_clicks=link.click_count,
        clicks_by_country=dict(clicks_by_country),
        recent_clicks=[ClickOut.model_validate(c) for c in recent],
    )


@router.get("/{code}")
async def get_analytics_dashboard(
    code: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    link = await _get_owned_link(code, current_user, db)
    clicks_by_country = Counter(c.country or "Unknown" for c in link.clicks)
    recent = sorted(link.clicks, key=lambda c: c.clicked_at, reverse=True)[:20]
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "link": link,
        "clicks_by_country": dict(clicks_by_country),
        "recent_clicks": recent,
    })
