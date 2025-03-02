"""Base scraper implementation for web crawling."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from src.utils.logging import get_logger

logger = get_logger(__name__)

class BaseScraper(ABC):
    """
    Base class for all web scrapers.
    
    This abstract class defines the interface that all specialized scrapers must implement.
    """
    
    def __init__(
        self, 
        name: str,
        rate_limit: float = 1.0,  # Default: 1 request per second
        proxy: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the scraper with common settings.
        
        Args:
            name: Unique name for the scraper
            rate_limit: Minimum seconds between requests
            proxy: Optional proxy to use for requests
            headers: Custom headers for HTTP requests
        """
        self.name = name
        self.rate_limit = rate_limit
        self.proxy = proxy
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.last_request_time = 0.0
    
    @abstractmethod
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape content from a single URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with scraped content and metadata
        """
        pass
    
    @abstractmethod
    async def extract_content(self, html: str) -> Dict[str, Any]:
        """
        Extract structured content from raw HTML.
        
        Args:
            html: Raw HTML content
            
        Returns:
            Dictionary with extracted content
        """
        pass
    
    async def scrape_multiple(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape content from multiple URLs with rate limiting.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of dictionaries with scraped content
        """
        results = []
        
        for url in urls:
            # Rate limiting
            now = datetime.now().timestamp()
            elapsed = now - self.last_request_time
            if elapsed < self.rate_limit:
                await asyncio.sleep(self.rate_limit - elapsed)
            
            try:
                result = await self.scrape_url(url)
                results.append(result)
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                results.append({"url": url, "error": str(e)})
            
            self.last_request_time = datetime.now().timestamp()
        
        return results
    
    async def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate scraped data for quality and completeness.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        # Base validation - check that we have some content
        if not data or "content" not in data or not data["content"]:
            return False
        
        # More sophisticated validation should be implemented by subclasses
        return True 