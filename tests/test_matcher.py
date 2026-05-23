from water_alerts.config import LocationConfig
from water_alerts.matcher import find_alert, keyword_matches_text
from water_alerts.models import ServicePost
from water_alerts.text import normalize_text


def test_normalize_matches_cyrillic_latin_and_diacritics() -> None:
    assert normalize_text("Нишка Бања") == normalize_text("Niška Banja")
    assert normalize_text("Заплањска") == normalize_text("Zaplanjska")


def test_find_alert_matches_configured_location() -> None:
    post = ServicePost(
        title="РАДОВИ У НИШКОЈ БАЊИ",
        url="https://example.test/post",
        content="Због радова у Заплањској улици могућ је прекид водоснабдевања до 15 часова.",
    )
    locations = (
        LocationConfig(
            name="Niska Banja / Zaplanjska",
            keywords=("Niska Banja", "Zaplanjska"),
        ),
    )

    alert = find_alert(post, locations)

    assert alert is not None
    assert alert.matches[0].name == "Niska Banja / Zaplanjska"
    assert set(alert.matches[0].matched_keywords) == {"Niska Banja", "Zaplanjska"}


def test_keyword_matches_inflected_location_forms() -> None:
    assert keyword_matches_text("Niska Banja", "Радови у Нишкој Бањи")
    assert keyword_matches_text("Zaplanjska", "квар у Заплањској улици")
