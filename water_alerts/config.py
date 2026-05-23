from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class LocationConfig:
    name: str
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class AppConfig:
    source_url: str
    max_posts: int
    request_timeout_seconds: int
    locations: tuple[LocationConfig, ...]
    email_subject_prefix: str


def load_config(path: str | Path = "config.yml") -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}. Copy config.example.yml to config.yml first."
        )

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    locations = tuple(
        LocationConfig(
            name=str(item["name"]),
            keywords=tuple(str(keyword) for keyword in item.get("keywords", [])),
        )
        for item in raw.get("locations", [])
    )

    if not locations:
        raise ValueError("At least one location must be configured.")

    return AppConfig(
        source_url=str(raw.get("source_url", "https://jkpnaissus.co.rs/servisne-informacije/")),
        max_posts=int(raw.get("max_posts", 10)),
        request_timeout_seconds=int(raw.get("request_timeout_seconds", 20)),
        locations=locations,
        email_subject_prefix=str(raw.get("email_subject_prefix", "[Vodovod]")),
    )

