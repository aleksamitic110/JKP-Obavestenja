from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.text import normalize_text
from app.models.location import Location
from app.models.scraped_item import ScrapedItem
from app.models.subscriber import Subscriber
from app.models.subscription import Subscription


async def match_item_to_subscriptions(
    session: AsyncSession,
    item: ScrapedItem,
) -> list[tuple[Subscriber, Subscription]]:
    """Find all (subscriber, subscription) pairs that match a scraped item."""
    searchable = " ".join(
        part for part in (item.title or "", item.content or "") if part
    )
    normalized_text = normalize_text(searchable)

    result = await session.execute(
        select(Subscription)
        .options(selectinload(Subscription.location))
        .where(Subscription.is_active == True)
    )
    subscriptions = result.scalars().all()

    matches: list[tuple[Subscriber, Subscription]] = []
    for sub in subscriptions:
        if _matches_subscription(normalized_text, sub):
            subscriber = await session.get(Subscriber, sub.subscriber_id)
            if subscriber and subscriber.is_active:
                matches.append((subscriber, sub))

    return matches


def _matches_subscription(normalized_text: str, subscription: Subscription) -> bool:
    if subscription.custom_keywords:
        for keyword in subscription.custom_keywords:
            if _keyword_matches(normalize_text(keyword), normalized_text):
                return True

    if subscription.location:
        location_name = normalize_text(subscription.location.name)
        if location_name and location_name in normalized_text:
            return True

    return False


def _keyword_matches(normalized_keyword: str, normalized_text: str) -> bool:
    if not normalized_keyword:
        return False
    if normalized_keyword in normalized_text:
        return True

    keyword_tokens = normalized_keyword.split()
    text_tokens = normalized_text.split()
    return all(
        any(_tokens_share_root(kw, txt) for txt in text_tokens)
        for kw in keyword_tokens
    )


def _tokens_share_root(token_a: str, token_b: str) -> bool:
    min_len = min(len(token_a), len(token_b))
    for length in range(min_len, 2, -1):
        if token_a[:length] == token_b[:length]:
            return True
    return False
