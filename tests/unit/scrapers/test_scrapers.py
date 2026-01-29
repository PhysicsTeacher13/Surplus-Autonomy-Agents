"""Unit tests for web scrapers."""

import pytest
from unittest.mock import Mock, MagicMock
import time

from surplus_agents.crawler.scrapers.base import BaseScraper
from surplus_agents.crawler.scrapers.county_scraper import CountyWebsiteScraper


class TestScraper(BaseScraper):
    """Concrete implementation for testing BaseScraper."""
    
    def scrape(self, url, **kwargs):
        self._rate_limit()
        return self._create_result({"test": "data"}, url)


@pytest.mark.unit
def test_base_scraper_initialization():
    """Test base scraper initialization."""
    scraper = TestScraper(mode="TEST", rate_limit_seconds=2.0, max_retries=5)
    
    assert scraper.mode == "TEST"
    assert scraper.rate_limit_seconds == 2.0
    assert scraper.max_retries == 5


@pytest.mark.unit
def test_base_scraper_rate_limiting():
    """Test rate limiting functionality."""
    scraper = TestScraper(mode="TEST", rate_limit_seconds=0.1)
    
    start_time = time.time()
    scraper.scrape("http://example.com")
    scraper.scrape("http://example.com")
    elapsed = time.time() - start_time
    
    # Should take at least rate_limit_seconds between requests
    assert elapsed >= 0.1


@pytest.mark.unit
def test_base_scraper_create_result():
    """Test result creation."""
    scraper = TestScraper(mode="TEST")
    
    result = scraper._create_result(
        data={"key": "value"},
        url="http://example.com",
        status="ok"
    )
    
    assert result["url"] == "http://example.com"
    assert result["status"] == "ok"
    assert result["data"]["key"] == "value"
    assert "metadata" in result
    assert result["metadata"]["mode"] == "TEST"


@pytest.mark.unit
def test_county_scraper_initialization():
    """Test county website scraper initialization."""
    scraper = CountyWebsiteScraper(mode="TEST")
    assert scraper.mode == "TEST"


@pytest.mark.unit
def test_county_scraper_test_mode_requires_fixtures():
    """Test that TEST mode requires fixtures."""
    scraper = CountyWebsiteScraper(mode="TEST")
    
    result = scraper.scrape("http://example.com")
    
    assert result["status"] == "error"
    assert "TEST mode requires fixtures" in result["error"] or "fixture_key" in result["error"]


@pytest.mark.unit
def test_county_scraper_with_fixtures():
    """Test county scraper with fixtures."""
    # Mock fixtures
    fixtures = Mock()
    fixtures.read_text.return_value = """
    <html>
        <body>
            <h1>County Website</h1>
            <div class="info">County Information</div>
        </body>
    </html>
    """
    
    scraper = CountyWebsiteScraper(mode="TEST", fixtures=fixtures)
    
    selectors = {
        "title": "h1",
        "info": ".info"
    }
    
    result = scraper.scrape(
        "http://example.com",
        fixture_key="county_page.html",
        selectors=selectors
    )
    
    assert result["status"] == "ok"
    assert result["data"]["title"] == "County Website"
    assert result["data"]["info"] == "County Information"


@pytest.mark.unit
def test_county_scraper_extract_data():
    """Test data extraction from HTML."""
    from bs4 import BeautifulSoup
    
    fixtures = Mock()
    fixtures.read_text.return_value = """
    <html>
        <body>
            <div class="property">Property 1</div>
            <div class="property">Property 2</div>
        </body>
    </html>
    """
    
    scraper = CountyWebsiteScraper(mode="TEST", fixtures=fixtures)
    
    selectors = {
        "properties": ".property"
    }
    
    result = scraper.scrape(
        "http://example.com",
        fixture_key="properties.html",
        selectors=selectors
    )
    
    assert result["status"] == "ok"
    # Multiple elements should be returned as list
    assert isinstance(result["data"]["properties"], list)
    assert len(result["data"]["properties"]) == 2


@pytest.mark.unit
def test_county_scraper_error_handling():
    """Test error handling in scraper."""
    fixtures = Mock()
    fixtures.read_text.side_effect = Exception("File not found")
    
    scraper = CountyWebsiteScraper(mode="TEST", fixtures=fixtures)
    
    result = scraper.scrape(
        "http://example.com",
        fixture_key="missing.html"
    )
    
    assert result["status"] == "error"
    assert "File not found" in result["error"]
