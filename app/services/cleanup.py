import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import delete

from app.database import SessionLocal
from app.models import Link

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def delete_expired_links():
    async with SessionLocal() as db:
        result = await db.execute(
            delete(Link).where(
                Link.expires_at < datetime.now(timezone.utc),
                Link.expires_at.isnot(None),
            )
        )
        await db.commit()
        count = result.rowcount
        if count:
            logger.info(f"Cleanup: deleted {count} expired link(s)")


def start_cleanup_scheduler():
    scheduler.add_job(delete_expired_links, "interval", hours=1, id="cleanup_expired")
    scheduler.start()
    logger.info("Cleanup scheduler started")
