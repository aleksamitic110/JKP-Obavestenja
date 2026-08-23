from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select

from app.database import async_session_factory
from app.models.scraper_source import ScraperSource
from app.models.scraped_item import ScrapedItem
from app.notifications.channels import EmailNotifier
from app.notifications.dispatch import dispatch_alerts
from app.scrapers.registry import get_scraper

LOGGER = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Europe/Belgrade")


async def run_scraper_job(source_id: int) -> None:
    """Main job: scrape source → store items → match → notify."""
    async with async_session_factory() as session:
        source = await session.get(ScraperSource, source_id)
        if not source or not source.is_active:
            return

        source.last_run_status = "running"
        await session.commit()

        try:
            scraper = get_scraper(source.scraper_key)
            posts = await scraper.fetch_latest(max_items=source.max_items)
            await scraper.close()

            new_items = 0
            notifiers = [EmailNotifier()]

            for post in posts:
                exists = await session.execute(
                    select(ScrapedItem).where(
                        ScrapedItem.source_id == source.id,
                        ScrapedItem.external_url == post.url,
                    )
                )
                if exists.scalar_one_or_none():
                    continue

                item = ScrapedItem(
                    source_id=source.id,
                    external_url=post.url,
                    title=post.title,
                    content=post.content,
                    published_at=post.published_at,
                )
                session.add(item)
                await session.flush()

                await dispatch_alerts(session, item, notifiers)
                new_items += 1

            source.last_run_at = datetime.now(timezone.utc)
            source.last_run_status = "ok"
            await session.commit()
            LOGGER.info("Scraper %s: %d new items", source.scraper_key, new_items)

        except Exception as e:
            source.last_run_status = "error"
            source.last_error = str(e)[:500]
            await session.commit()
            LOGGER.exception("Scraper %s failed", source.scraper_key)


async def sync_schedule_async() -> None:
    """Read active sources from DB and update APScheduler jobs."""
    async with async_session_factory() as session:
        sources = await session.execute(
            select(ScraperSource).where(ScraperSource.is_active == True)
        )
        for source in sources.scalars().all():
            job_id = f"scraper_{source.id}"
            existing = scheduler.get_job(job_id)
            if existing:
                existing.remove()
            scheduler.add_job(
                run_scraper_job,
                trigger=IntervalTrigger(minutes=source.interval_minutes),
                args=[source.id],
                id=job_id,
                name=f"Scraper: {source.name}",
                replace_existing=True,
                next_run_time=datetime.now(timezone.utc),
            )
            LOGGER.info("Scheduled %s every %d minutes", source.name, source.interval_minutes)
