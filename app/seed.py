"""Seed the locations table with Niš neighborhoods and streets."""
from __future__ import annotations

import asyncio
import re
import unicodedata

from sqlalchemy import select

from app.database import Base, async_session_factory, engine
from app.models.location import Location

NIS_LOCATIONS = [
    {"name": "Niš", "level": "city", "lat": 43.3209, "lon": 21.8958, "children": [
        {"name": "Mediana", "level": "municipality", "lat": 43.3167, "lon": 21.9000, "children": [
            {"name": "Bulevar 12. februar", "level": "street", "lat": 43.3150, "lon": 21.8980},
            {"name": "Knjaza Miloša", "level": "street", "lat": 43.3180, "lon": 21.8960},
            {"name": "Vožda Karađorđa", "level": "street", "lat": 43.3200, "lon": 21.8940},
        ]},
        {"name": "Pantelej", "level": "municipality", "lat": 43.3350, "lon": 21.9100, "children": [
            {"name": "Pantelejsko polje", "level": "area", "lat": 43.3400, "lon": 21.9150},
        ]},
        {"name": "Palilula", "level": "municipality", "lat": 43.3100, "lon": 21.8800},
        {"name": "Crveni Krst", "level": "municipality", "lat": 43.3300, "lon": 21.8700},
        {"name": "Niška Banja", "level": "municipality", "lat": 43.3500, "lon": 21.9300},
        {"name": "Ledena Stena", "level": "area", "lat": 43.3050, "lon": 21.8600},
        {"name": "Durlan", "level": "area", "lat": 43.3000, "lon": 21.8500},
    ]},
]


def _slugify(name: str) -> str:
    value = unicodedata.normalize("NFKD", name)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
    return re.sub(r"\s+", " ", value)


async def seed_locations() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        for city_data in NIS_LOCATIONS:
            city = Location(
                name=city_data["name"],
                name_ascii=_slugify(city_data["name"]),
                city=city_data["name"],
                level=city_data["level"],
                lat=city_data.get("lat"),
                lon=city_data.get("lon"),
            )
            session.add(city)
            await session.flush()

            for child_data in city_data.get("children", []):
                child = Location(
                    name=child_data["name"],
                    name_ascii=_slugify(child_data["name"]),
                    city=city_data["name"],
                    level=child_data["level"],
                    lat=child_data.get("lat"),
                    lon=child_data.get("lon"),
                    parent_id=city.id,
                )
                session.add(child)
                await session.flush()

                for grandchild_data in child_data.get("children", []):
                    grandchild = Location(
                        name=grandchild_data["name"],
                        name_ascii=_slugify(grandchild_data["name"]),
                        city=city_data["name"],
                        level=grandchild_data["level"],
                        lat=grandchild_data.get("lat"),
                        lon=grandchild_data.get("lon"),
                        parent_id=child.id,
                    )
                    session.add(grandchild)

        await session.commit()
        print("Locations seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed_locations())
