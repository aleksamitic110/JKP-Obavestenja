from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ScrapedPost:
    """Unified output from all scrapers."""
    title: str
    url: str
    content: str
    published_at: str | None = None
    metadata: dict = field(default_factory=dict)


class ScraperBase(ABC):
    """
    Every scraper implements this interface.
    To add a new utility:
      1. Create scrapers/implementations/my_utility.py
      2. Class inherits ScraperBase
      3. Implement fetch_latest()
      4. Register in registry.py
      5. Add DB row to scraper_sources
    """

    @abstractmethod
    async def fetch_latest(self, max_items: int = 20) -> list[ScrapedPost]:
        """Fetch latest posts from the source. Return newest first."""
        ...

    async def close(self) -> None:
        """Cleanup resources. Override if needed."""
        pass
