from app.scrapers.base import ScrapedPost, ScraperBase
from app.scrapers.registry import get_scraper, list_scrapers, register


def test_scraped_post_fields() -> None:
    post = ScrapedPost(title="Test", url="https://example.com", content="Body")
    assert post.title == "Test"
    assert post.published_at is None
    assert post.metadata == {}


def test_register_and_get_scraper() -> None:
    @register("test_scraper")
    class TestScraper(ScraperBase):
        async def fetch_latest(self, max_items: int = 20):
            return []

    assert "test_scraper" in list_scrapers()
    scraper = get_scraper("test_scraper")
    assert isinstance(scraper, TestScraper)


def test_get_unknown_scraper_raises() -> None:
    try:
        get_scraper("nonexistent")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "nonexistent" in str(e)
