"""Base scraper class for web scraping operations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import time
from datetime import datetime, timezone


class BaseScraper(ABC):
    """
    Base class for all web scrapers.
    
    Provides common functionality like rate limiting, retry logic,
    and standardized output format.
    """
    
    def __init__(
        self,
        mode: str = "TEST",
        rate_limit_seconds: float = 1.0,
        max_retries: int = 3
    ):
        """
        Initialize scraper.
        
        Args:
            mode: Operating mode (TEST, DRY_RUN, LIVE)
            rate_limit_seconds: Minimum seconds between requests
            max_retries: Maximum retry attempts for failed requests
        """
        self.mode = mode
        self.rate_limit_seconds = rate_limit_seconds
        self.max_retries = max_retries
        self.last_request_time = 0.0
    
    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        if self.rate_limit_seconds > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit_seconds:
                time.sleep(self.rate_limit_seconds - elapsed)
        self.last_request_time = time.time()
    
    @abstractmethod
    def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Scrape data from URL.
        
        Args:
            url: URL to scrape
            **kwargs: Additional scraping parameters
            
        Returns:
            Dictionary containing scraped data
        """
        pass
    
    def _create_result(
        self,
        data: Dict[str, Any],
        url: str,
        status: str = "ok",
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create standardized result dictionary.
        
        Args:
            data: Scraped data
            url: Source URL
            status: Result status ("ok", "error", "partial")
            error: Error message if any
            
        Returns:
            Standardized result dictionary
        """
        return {
            "url": url,
            "status": status,
            "data": data,
            "error": error,
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "mode": self.mode,
                "scraper": self.__class__.__name__
            }
        }
