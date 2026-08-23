# Serbia Utility Alerts

Bespлатна platforma za obaveštavanje građana Srbije o prekidima vode, struje i drugih komunalnih usluga.

Korisnici se prijavljuju putem email-a biraju lokaciju na mapi i primaju obaveštenja kada dođe do prekida u njihovom području.

## Arhitektura

```
app/
├── core/                    # Deljena logika (normalizacija teksta, matchovanje)
├── scrapers/                # Plugin sistem za skupljanje podataka
│   ├── base.py              # Apstraktna klasa za sve scrapere
│   ├── registry.py          # Auto-registracija scrapera
│   └── implementations/     # Konkretni scraperi (Naissus voda, EDS struja, ...)
├── notifications/           # Plugin sistem za slanje obaveštenja
│   ├── base.py              # Apstraktna klasa za sve kanale
│   ├── dispatch.py          # Logika usklađivanja i slanja
│   └── channels/            # Konkretni kanali (email, telegram, discord, ...)
├── models/                  # SQLAlchemy ORM modeli
├── routes/                  # FastAPI rute (web + API)
├── templates/               # Jinja2 HTML šablone
├── scheduler.py             # APScheduler — zakazivanje scrapera
├── config.py                # Podešavanja iz .env
├── database.py              # Async SQLAlchemy engine
└── main.py                  # FastAPI aplikacija
```

## Pokretanje

```bash
pip install -r requirements.txt
cp .env.example .env
# Popuni .env podatke
uvicorn app.main:app --reload
```

## Docker

```bash
docker compose up --build
```

Pokreće: FastAPI (port 8000) + PostgreSQL 16 + Caddy (port 80).

## Dodavanje novog scrapera

1. Kopiraj `app/scrapers/implementations/_template.py`
2. Implementiraj `fetch_latest()`
3. Dodaj `@register("moj_ključ")`
4. Importuj u `implementations/__init__.py`
5. Dodaj red u `scraper_sources` tabelu

## Dodavanje novog kanala obaveštenja

1. Napravi `app/notifications/channels/moj_kanal.py`
2. Nasledi `NotifierBase`, implementiraj `send()`
3. Dodaj u `channels/__init__.py`
