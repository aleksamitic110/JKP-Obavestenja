# AGENTS.md — Serbia Utility Alerts

Read this at the start of every session to restore full project context.

## What This Is

Free, modular, multi-utility notification platform for Serbian citizens. Users subscribe via email + location (map or dropdown) to receive alerts about water/power interruptions. Runs entirely on Oracle Cloud Always Free Tier — zero hosting cost.

**Target audience:** Citizens of Niš, Serbia (expanding to other cities later).

## Tech Stack

- **Backend:** Python 3.12+ / FastAPI
- **Templates:** Jinja2 + HTMX + Alpine.js (no React — saves RAM on 1GB free VM)
- **CSS:** Tailwind CSS via CDN
- **Map:** Leaflet.js + OpenStreetMap (free, no API key)
- **Database:** PostgreSQL 16 (Oracle Always Free Autonomous DB)
- **ORM:** SQLAlchemy 2.0 async + Alembic migrations
- **Scheduler:** APScheduler (in-process, per-source intervals)
- **Email:** SMTP (Gmail app-password)
- **Containerization:** Docker + Docker Compose
- **Reverse Proxy:** Caddy (auto-HTTPS)
- **Hosting:** Oracle Cloud Always Free VM (AMD, 1GB RAM)

## Architecture

```
Internet → Caddy (HTTPS) → FastAPI (port 8000) → PostgreSQL
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                scrapers/  notifications/  routes/
                (plugins)  (channels)     (web + API)
```

All on one Docker Compose stack. Three containers: app, PostgreSQL, Caddy.

## Project Structure

```
app/
├── core/                      # Shared logic (no external deps)
│   ├── text.py                # Cyrillic/Latin normalization, diacritics
│   └── matcher.py             # Match scraped items → subscriber prefs
├── scrapers/                  # Plugin system for data collection
│   ├── base.py                # ScraperBase ABC + ScrapedPost dataclass
│   ├── registry.py            # @register("key") decorator + get/list
│   └── implementations/       # One file per utility/city
│       └── _template.py       # Copy-paste template for new scrapers
├── notifications/             # Plugin system for delivery
│   ├── base.py                # NotifierBase ABC + NotificationMessage
│   ├── dispatch.py            # Match + fan-out to all channels
│   └── channels/              # One file per channel
│       └── email.py           # SMTP email sender
├── models/                    # SQLAlchemy ORM (6 tables)
│   ├── location.py            # City > municipality > street hierarchy
│   ├── subscriber.py          # Email subscribers + UUID token
│   ├── subscription.py        # subscriber → location + custom_keywords
│   ├── scraper_source.py      # Scraper config per utility/city
│   ├── scraped_item.py        # Deduplicated scraped content
│   └── notification_log.py    # Audit trail of sent alerts
├── routes/                    # FastAPI routers (empty — Phase 3)
├── templates/                 # Jinja2 HTML (base, index, success, unsubscribe, admin)
├── scheduler.py               # APScheduler setup + job runner
├── config.py                  # Pydantic Settings (reads .env)
├── database.py                # Async SQLAlchemy engine + session factory
├── seed.py                    # Seed Niš locations into DB
└── main.py                    # FastAPI app entry point + lifespan
```

## Database Schema (6 tables)

| Table | Purpose |
|-------|---------|
| `locations` | Hierarchical catalog (city > municipality > street). Has lat/lon for map. |
| `subscribers` | Email + is_active + UUID token for unsubscribe link |
| `subscriptions` | Links subscriber → location OR custom_keywords + utility_types |
| `scraper_sources` | One row per scraper: key, city, URL, interval, status |
| `scraped_items` | Every scraped post. Unique on (source_id, external_url) for dedup |
| `notification_log` | Every sent notification. Unique on (subscriber_id, item_id, channel) |

Migration: `alembic/versions/001_initial_schema.py`

## Plugin Interfaces

### Adding a New Scraper

1. Copy `app/scrapers/implementations/_template.py` → `my_utility.py`
2. Rename class, change `@register("my_key")`
3. Implement `async def fetch_latest(self, max_items) -> list[ScrapedPost]`
4. Import in `implementations/__init__.py`
5. Add DB row: `INSERT INTO scraper_sources (name, scraper_key, city, utility_type, url, interval_minutes) VALUES (...)`
6. Done — scheduler auto-picks it up

### Adding a New Notification Channel

1. Create `app/notifications/channels/telegram.py`
2. Class inherits `NotifierBase`, implement `channel_name` + `send()`
3. Import in `channels/__init__.py`
4. Add recipient field to `subscribers` table if needed
5. Update `dispatch.py` `_get_recipient()` for new channel

## Environment Variables (.env)

```
DATABASE_URL=postgresql+asyncpg://alerts:alerts@db:5432/serbia_alerts
DB_PASSWORD=alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...  (Google App Password, not regular password)
SMTP_FROM=...
APP_URL=http://localhost:8000
ADMIN_PASSWORD=...
SECRET_KEY=...
TIMEZONE=Europe/Belgrade
```

## Conventions

- All Python files use `from __future__ import annotations`
- Async everywhere (asyncpg, httpx, AsyncSession)
- Frozen dataclasses for value objects (ScrapedPost, NotificationMessage)
- Abstract base classes for plugin interfaces (ScraperBase, NotifierBase)
- No comments unless asked
- Follow existing code style in each file
- Tests in `tests/` mirror `app/` structure

## Commands

```bash
# Local dev
pip install -r requirements.txt
cp .env.example .env  # fill in values
uvicorn app.main:app --reload

# Docker
docker compose up --build

# Tests
python -m pytest tests/ -v

# Seed locations
python -m app.seed

# Alembic migrations
alembic upgrade head
alembic revision --autogenerate -m "description"
```

## Completed Work

### Phase 1: Project Scaffold ✅
- FastAPI app with lifespan (startup creates tables, starts scheduler)
- Pydantic Settings reading from .env
- Async SQLAlchemy engine + session factory
- All 6 ORM models with relationships and indexes
- Alembic setup with first migration (001_initial_schema)
- Docker Compose (app + PostgreSQL 16 + Caddy)
- Dockerfile (Python 3.12 slim)
- Caddyfile (reverse proxy)
- Seed script for Niš locations
- 6 Jinja2 templates (base, index, success, unsubscribe, admin/login, admin/dashboard)
- Leaflet map init in static/js/map.js
- Health endpoint at GET /health
- All 8 tests passing
- Clean modular structure: core/, scrapers/, notifications/, models/, routes/

### Cleanup Done ✅
- Deleted old MVP (water_alerts/, config.yml, .github/, docs/, data/)
- Restructured for modularity: scrapers/ and notifications/ as independent packages
- Shared logic in core/ package
- Rewrote README.md

## Next: Phase 2 — Scraper Framework + Naissus Port

**Goal:** First real scraper running inside new architecture.

**Tasks:**
1. Port `water_alerts/scraper.py` logic → `app/scrapers/implementations/naissus_water.py`
   - Use httpx (async) instead of requests (sync)
   - Same BeautifulSoup parsing logic (DATE_RE, link extraction, content fetch)
   - Implement `ScraperBase.fetch_latest()`
2. Register in `implementations/__init__.py`
3. Seed `scraper_sources` table with Naissus water row
4. Verify scheduler runs scraper, items appear in `scraped_items` table

**Key reference:** The old `water_alerts/scraper.py` was deleted but its logic is documented in PLAN.md section 6.3 (NaissusWaterScraper example). The scraping approach:
- Fetch `https://jkpnaissus.co.rs/servisne-informacije/`
- Find all `<a>` tags containing dates matching `DD.MM.YYYY | HH:MM`
- Extract URL, title, published_at
- Fetch each post's full content from its page
- Return as ScrapedPost list

## Future Phases

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1 | ✅ Done | Project scaffold, DB, Docker |
| Phase 2 | 🔲 Next | Scraper framework + Naissus water port |
| Phase 3 | 🔲 Pending | Subscription frontend (form + Leaflet map) |
| Phase 4 | 🔲 Pending | Email notification dispatch |
| Phase 5 | 🔲 Pending | EDS Niš power scraper |
| Phase 6 | 🔲 Pending | Admin dashboard |
| Phase 7 | 🔲 Pending | Deploy to Oracle Cloud |
| Phase 8 | 🔲 Pending | Telegram/Discord channels |

## Agent skills

### Issue tracker

Issues live in GitHub Issues (`aleksamitic110/JKP-Obavestenja`), managed via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default canonical triage label vocabulary (labels equal their role names). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` at repo root + `docs/adr/`. See `docs/agents/domain.md`.
