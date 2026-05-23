from __future__ import annotations

import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from water_alerts.models import ServicePost
from water_alerts.text import compact_preview


DATE_RE = re.compile(r"\b\d{2}\.\d{2}\.\d{4}\s*\|\s*\d{2}:\d{2}\b")


class NaissusScraper:
    def __init__(self, source_url: str, timeout_seconds: int = 20) -> None:
        self.source_url = source_url
        self.timeout_seconds = timeout_seconds
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "VodovodObavestenja/0.1 "
                    "(personal notification scraper; contact: local-user)"
                )
            }
        )

    def fetch_latest_posts(self, max_posts: int = 10) -> list[ServicePost]:
        html = self._get(self.source_url)
        soup = BeautifulSoup(html, "html.parser")

        posts: list[ServicePost] = []
        seen: set[str] = set()
        for link in soup.find_all("a", href=True):
            text = link.get_text(" ", strip=True)
            if not DATE_RE.search(text):
                continue

            url = urljoin(self.source_url, link["href"])
            if url in seen:
                continue

            seen.add(url)
            published_at = DATE_RE.search(text)
            clean_text = re.sub(DATE_RE, "", text).strip(" -|")
            posts.append(
                ServicePost(
                    title=clean_text or "Servisna informacija",
                    url=url,
                    published_at=published_at.group(0) if published_at else None,
                    excerpt=compact_preview(clean_text, limit=300),
                )
            )
            if len(posts) >= max_posts:
                break

        return posts

    def fetch_post_details(self, post: ServicePost) -> ServicePost:
        html = self._get(post.url)
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript", "svg", "form"]):
            tag.decompose()

        title = _extract_title(soup) or post.title
        published_at = _extract_date(soup) or post.published_at
        content = _extract_content(soup)

        return ServicePost(
            title=title,
            url=post.url,
            published_at=published_at,
            excerpt=post.excerpt,
            content=content,
        )

    def _get(self, url: str) -> str:
        response = self.session.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response.text


def _extract_title(soup: BeautifulSoup) -> str | None:
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(" ", strip=True)
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        return str(og_title["content"]).strip()
    return None


def _extract_date(soup: BeautifulSoup) -> str | None:
    text = soup.get_text(" ", strip=True)
    match = DATE_RE.search(text)
    return match.group(0) if match else None


def _extract_content(soup: BeautifulSoup) -> str:
    candidates = soup.select(
        ".entry-content.is-layout-constrained, "
        ".elementor-widget-theme-post-content, "
        ".post-content, "
        "article, "
        "main"
    )
    for candidate in candidates:
        text = _clean_article_text(candidate.get_text("\n", strip=True))
        if len(text) > 80:
            return text

    full_text = _clean_article_text(soup.get_text("\n", strip=True))
    marker = "Подели вест"
    if marker in full_text:
        full_text = full_text.split(marker, 1)[1]
    footer_marker = "ПОЗИВНИ ЦЕНТАР"
    if footer_marker in full_text:
        full_text = full_text.split(footer_marker, 1)[0]
    return full_text.strip()


def _clean_article_text(value: str) -> str:
    value = re.split(r"\bPrevious\s+Post\b", value, maxsplit=1)[0]
    value = re.split(r"\bNext\s+Post\b", value, maxsplit=1)[0]
    ignored_prefixes = (
        "Share on",
        "Image:",
        "Image",
    )
    lines = []
    for raw_line in value.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if any(line.startswith(prefix) for prefix in ignored_prefixes):
            continue
        lines.append(line)
    return "\n".join(lines)
