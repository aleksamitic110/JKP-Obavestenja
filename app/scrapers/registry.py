from __future__ import annotations

from app.scrapers.base import ScraperBase

_REGISTRY: dict[str, type[ScraperBase]] = {}


def register(key: str):
    """Decorator to register a scraper class."""
    def decorator(cls: type[ScraperBase]):
        _REGISTRY[key] = cls
        return cls
    return decorator


def get_scraper(key: str) -> ScraperBase:
    """Instantiate a registered scraper by key."""
    cls = _REGISTRY.get(key)
    if cls is None:
        raise ValueError(f"Unknown scraper key: {key}. Registered: {list(_REGISTRY.keys())}")
    return cls()


def list_scrapers() -> list[str]:
    """Return all registered scraper keys."""
    return sorted(_REGISTRY.keys())
