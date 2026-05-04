import secrets
import string

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Link

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6


async def generate_unique_code(db: AsyncSession) -> str:
    for _ in range(10):
        code = "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))
        result = await db.execute(select(Link).where(Link.code == code))
        if result.scalar_one_or_none() is None:
            return code
    raise RuntimeError("Failed to generate a unique short code after 10 attempts")
