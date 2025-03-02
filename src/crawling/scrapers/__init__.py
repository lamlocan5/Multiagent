"""Web scraping components for data acquisition."""

from typing import Type, Dict, Any
from src.crawling.scrapers.base import BaseScraper

# Registry of available scrapers
SCRAPERS: Dict[str, Type[BaseScraper]] = {}

def register_scraper(name: str, scraper_class: Type[BaseScraper]) -> None:
    """
    Register a scraper class with a name.
    
    Args:
        name: Unique name for the scraper
        scraper_class: The scraper class to register
    """
    SCRAPERS[name] = scraper_class

def get_scraper(name: str, **kwargs: Any) -> BaseScraper:
    """
    Get a scraper instance by name.
    
    Args:
        name: Name of the registered scraper
        **kwargs: Arguments to pass to the scraper constructor
    
    Returns:
        Initialized scraper instance
    
    Raises:
        ValueError: If no scraper with the given name is registered
    """
    if name not in SCRAPERS:
        raise ValueError(f"No scraper registered with name: {name}")
    
    return SCRAPERS[name](**kwargs) 