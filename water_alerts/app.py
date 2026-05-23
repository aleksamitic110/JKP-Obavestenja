from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

from water_alerts.config import load_config
from water_alerts.matcher import find_alert
from water_alerts.notifiers import EmailNotifier, EmailSettings
from water_alerts.scraper import NaissusScraper
from water_alerts.storage import JsonStateStore


LOGGER = logging.getLogger(__name__)


def run(
    config_path: str = "config.yml",
    state_path: str = "data/state.json",
    dry_run: bool = False,
    notify: bool = True,
) -> int:
    load_dotenv()
    config = load_config(config_path)
    store = JsonStateStore(state_path)
    processed_urls = store.get_processed_urls()
    scraper = NaissusScraper(config.source_url, config.request_timeout_seconds)

    latest_posts = scraper.fetch_latest_posts(max_posts=config.max_posts)
    LOGGER.info("Found %s posts on source page.", len(latest_posts))

    new_processed_urls: set[str] = set()
    alerts_sent = 0
    notifier = None
    if notify and not dry_run:
        notifier = EmailNotifier(EmailSettings.from_env(), config.email_subject_prefix)

    for post in reversed(latest_posts):
        if post.url in processed_urls:
            continue

        detailed_post = scraper.fetch_post_details(post)
        alert = find_alert(detailed_post, config.locations)
        new_processed_urls.add(post.url)

        if not alert:
            LOGGER.info("No match: %s", detailed_post.url)
            continue

        LOGGER.info("Matched post: %s", detailed_post.url)
        alerts_sent += 1
        if dry_run:
            print(_format_dry_run_alert(alert))
        elif notifier:
            notifier.send(alert)

    if new_processed_urls and not dry_run:
        store.mark_processed(new_processed_urls)
        LOGGER.info("State updated: %s", Path(state_path))

    LOGGER.info("Done. Alerts: %s. Newly processed posts: %s.", alerts_sent, len(new_processed_urls))
    return 0


def _format_dry_run_alert(alert) -> str:
    keywords = ", ".join(
        keyword for match in alert.matches for keyword in match.matched_keywords
    )
    sections = "\n\n".join(alert.matched_sections) if alert.matched_sections else alert.content_preview
    return (
        "\n--- ALERT TEST ---\n"
        f"Naslov: {alert.post.title}\n"
        f"Datum: {alert.post.published_at or 'nije pronadjen'}\n"
        f"Poklapanja: {keywords}\n"
        f"Link: {alert.post.url}\n"
        f"Tekst: {sections}\n"
    )


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="JKP Naissus water outage notifier")
    parser.add_argument("--config", default="config.yml")
    parser.add_argument("--state", default="data/state.json")
    parser.add_argument("--dry-run", action="store_true", help="Print matches without sending email or writing state.")
    parser.add_argument("--no-notify", action="store_true", help="Run scraper and update state without sending email.")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(levelname)s %(message)s",
    )
    raise SystemExit(
        run(
            config_path=args.config,
            state_path=args.state,
            dry_run=args.dry_run,
            notify=not args.no_notify,
        )
    )


if __name__ == "__main__":
    main()
