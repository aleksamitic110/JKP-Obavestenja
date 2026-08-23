from app.core.text import normalize_text


def test_normalize_matches_cyrillic_latin_and_diacritics() -> None:
    assert normalize_text("Нишка Бања") == normalize_text("Niška Banja")
    assert normalize_text("Заплањска") == normalize_text("Zaplanjska")


def test_normalize_lowercases() -> None:
    assert normalize_text("HELLO WORLD") == "hello world"


def test_normalize_strips_diacritics() -> None:
    assert normalize_text("Niška") == "niska"
    assert normalize_text("Ćuprija") == "cuprija"
