from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user, get_redis, rate_limit
from app.models import User, Link
from app.schemas import LinkCreate, LinkOut
from app.services.shortener import generate_unique_code

router = APIRouter(prefix="/links", tags=["links"])


def build_link_out(link: Link) -> LinkOut:
    return LinkOut(
        id=link.id,
        code=link.code,
        original_url=link.original_url,
        short_url=f"{settings.base_url}/{link.code}",
        click_count=link.click_count,
        created_at=link.created_at,
        expires_at=link.expires_at,
    )


@router.post("/", response_model=LinkOut, status_code=status.HTTP_201_CREATED)
async def create_link(
    payload: LinkCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis=Depends(get_redis),
):
    await rate_limit(f"create:{current_user.id}", limit=20, window=60, redis=redis)

    code = payload.custom_code or await generate_unique_code(db)

    if payload.custom_code:
        existing = await db.execute(select(Link).where(Link.code == code))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Custom code already taken")

    link = Link(
        code=code,
        original_url=str(payload.original_url),
        owner_id=current_user.id,
        expires_at=payload.expires_at,
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return build_link_out(link)


@router.get("/", response_model=list[LinkOut])
async def list_links(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Link).where(Link.owner_id == current_user.id))
    return [build_link_out(link) for link in result.scalars().all()]


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Link).where(Link.code == code, Link.owner_id == current_user.id)
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    await db.delete(link)
    await db.commit()
