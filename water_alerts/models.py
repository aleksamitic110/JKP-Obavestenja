from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ServicePost:
    title: str
    url: str
    published_at: str | None = None
    excerpt: str | None = None
    content: str | None = None


@dataclass(frozen=True)
class LocationMatch:
    name: str
    keywords: tuple[str, ...]
    matched_keywords: tuple[str, ...]


@dataclass(frozen=True)
class Alert:
    post: ServicePost
    matches: tuple[LocationMatch, ...]
    content_preview: str
    matched_sections: tuple[str, ...] = field(default_factory=tuple)

