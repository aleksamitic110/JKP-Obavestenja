from __future__ import annotations

from datetime import datetime

from sqlalchemy import ARRAY, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subscriber_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subscribers.id", ondelete="CASCADE"), nullable=False
    )
    location_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("locations.id", ondelete="SET NULL"), nullable=True
    )
    custom_keywords: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    utility_types: Mapped[list[str]] = mapped_column(
        ARRAY(Text), default=["water", "power"]
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    subscriber: Mapped["Subscriber"] = relationship("Subscriber")  # noqa: F821
    location: Mapped["Location | None"] = relationship("Location")  # noqa: F821
