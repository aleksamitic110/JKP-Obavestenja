from __future__ import annotations

from water_alerts.config import LocationConfig
from water_alerts.models import Alert, LocationMatch, ServicePost
from water_alerts.text import compact_preview, normalize_text, split_sections


def keyword_matches_text(keyword: str, text: str) -> bool:
    normalized_keyword = normalize_text(keyword)
    normalized_text = normalize_text(text)
    if not normalized_keyword:
        return False
    if normalized_keyword in normalized_text:
        return True

    keyword_tokens = normalized_keyword.split()
    text_tokens = normalized_text.split()
    return all(
        any(_tokens_share_location_root(keyword_token, text_token) for text_token in text_tokens)
        for keyword_token in keyword_tokens
    )


def find_alert(post: ServicePost, locations: tuple[LocationConfig, ...]) -> Alert | None:
    searchable = "\n".join(
        part for part in (post.title, post.excerpt or "", post.content or "") if part
    )

    matches: list[LocationMatch] = []
    for location in locations:
        matched_keywords = tuple(
            keyword
            for keyword in location.keywords
            if keyword_matches_text(keyword, searchable)
        )
        if matched_keywords:
            matches.append(
                LocationMatch(
                    name=location.name,
                    keywords=location.keywords,
                    matched_keywords=matched_keywords,
                )
            )

    if not matches:
        return None

    sections = _matched_sections(post.content or searchable, matches)
    return Alert(
        post=post,
        matches=tuple(matches),
        content_preview=compact_preview(post.content or searchable),
        matched_sections=tuple(sections),
    )


def _matched_sections(content: str, matches: list[LocationMatch]) -> list[str]:
    keywords = [keyword for match in matches for keyword in match.matched_keywords]
    result: list[str] = []
    for section in split_sections(content):
        if any(keyword_matches_text(keyword, section) for keyword in keywords):
            result.append(compact_preview(section, limit=700))
    return result[:5]


def _tokens_share_location_root(left: str, right: str) -> bool:
    if len(left) < 4 or len(right) < 4:
        return left == right
    return left[:4] == right[:4]
