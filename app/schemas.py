from datetime import datetime
from pydantic import BaseModel, EmailStr, HttpUrl


# ── Auth ──────────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Links ─────────────────────────────────────────────
class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_code: str | None = None
    expires_at: datetime | None = None


class LinkOut(BaseModel):
    id: str
    code: str
    original_url: str
    short_url: str
    click_count: int
    created_at: datetime
    expires_at: datetime | None

    model_config = {"from_attributes": True}


# ── Analytics ─────────────────────────────────────────
class ClickOut(BaseModel):
    clicked_at: datetime
    country: str | None
    referrer: str | None
    user_agent: str | None

    model_config = {"from_attributes": True}


class AnalyticsSummary(BaseModel):
    code: str
    original_url: str
    total_clicks: int
    clicks_by_country: dict[str, int]
    recent_clicks: list[ClickOut]
