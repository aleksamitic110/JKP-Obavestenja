"""
TEMPLATE — Copy this file to create a new scraper.

Steps:
1. Copy this file: cp _template.py my_utility.py
2. Rename the class and update SCRAPER_KEY
3. Implement fetch_latest()
4. Add @register("my_utility_key") decorator
5. Import this file in implementations/__init__.py
6. Add a row to scraper_sources table with scraper_key = "my_utility_key"
"""
from __future__ import annotations

import httpx
from bs4 import BeautifulSoup

from app.scrapers.base import ScraperBase, ScrapedPost
from app.scrapers.registry import register


@register("my_utility_key")
class MyUtilityScraper(ScraperBase):
    """Description of what this scraper does."""

    SOURCE_URL = "https://example.rs/notices/"

    async def fetch_latest(self, max_items: int = 20) -> list[ScrapedPost]:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(self.SOURCE_URL)
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        posts: list[ScrapedPost] = []

        # TODO: Implement parsing logic
        # for item in soup.select(".some-selector"):
        #     posts.append(ScrapedPost(
        #         title=item.select_one(".title").get_text(strip=True),
        #         url=item["href"],
        #         content=item.select_one(".content").get_text(strip=True),
        #     ))
        #     if len(posts) >= max_items:
        #         break

        return posts
