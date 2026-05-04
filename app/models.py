from datetime import datetime, timezone
import uuid

from sqlalchemy import String, DateTime, ForeignKey, Integer, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    links: Mapped[list["Link"]] = relationship("Link", back_populates="owner", cascade="all, delete-orphan")


class Link(Base):
    __tablename__ = "links"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    owner_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    click_count: Mapped[int] = mapped_column(Integer, default=0)

    owner: Mapped["User"] = relationship("User", back_populates="links")
    clicks: Mapped[list["Click"]] = relationship("Click", back_populates="link", cascade="all, delete-orphan")


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    link_id: Mapped[str] = mapped_column(String, ForeignKey("links.id"), nullable=False)
    clicked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    referrer: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)

    link: Mapped["Link"] = relationship("Link", back_populates="clicks")
