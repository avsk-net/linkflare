from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as aioredis

from app.config import settings
from app.database import get_db
from app.models import User

bearer_scheme = HTTPBearer()
_redis_client = None


async def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


async def rate_limit(key: str, limit: int, window: int, redis=None):
    """Generic rate limiter. Raises 429 if exceeded."""
    if redis is None:
        return
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, window)
    if current > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")
