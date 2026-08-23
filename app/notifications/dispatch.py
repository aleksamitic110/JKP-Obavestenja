from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.matcher import match_item_to_subscriptions
from app.models.notification_log import NotificationLog
from app.models.scraped_item import ScrapedItem
from app.models.subscription import Subscription
from app.notifications.base import NotifierBase, NotificationMessage

LOGGER = logging.getLogger(__name__)


@dataclass
class DispatchResult:
    sent: int = 0
    failed: int = 0
    skipped: int = 0


async def dispatch_alerts(
    session: AsyncSession,
    item: ScrapedItem,
    notifiers: list[NotifierBase],
) -> DispatchResult:
    """Find matching subscribers and send notifications through all channels."""
    result = DispatchResult()

    matching_subs = await match_item_to_subscriptions(session, item)

    for subscriber, subscription in matching_subs:
        existing = await session.execute(
            select(NotificationLog).where(
                NotificationLog.subscriber_id == subscriber.id,
                NotificationLog.item_id == item.id,
            )
        )
        if existing.scalar_one_or_none():
            result.skipped += 1
            continue

        message = _build_message(item)

        for notifier in notifiers:
            recipient = _get_recipient(subscriber, notifier.channel_name)
            if not recipient:
                continue

            sent = await notifier.send(recipient, message)
            log = NotificationLog(
                subscriber_id=subscriber.id,
                item_id=item.id,
                channel=notifier.channel_name,
                status="sent" if sent else "failed",
            )
            session.add(log)

            if sent:
                result.sent += 1
            else:
                result.failed += 1

    await session.commit()
    return result


def _build_message(item: ScrapedItem) -> NotificationMessage:
    subject = f"[Obaveštenje] {item.title}"
    body = f"{item.title}\n\n{item.content}\n\nViše: {item.external_url}"
    html_body = (
        f"<h2>{item.title}</h2>"
        f"<p>{item.content}</p>"
        f"<p><a href='{item.external_url}'>Više informacija</a></p>"
    )
    return NotificationMessage(subject=subject, body=body, html_body=html_body)


def _get_recipient(subscriber, channel: str) -> str | None:
    if channel == "email":
        return subscriber.email
    return None
