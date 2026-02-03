"""
Scraper Factory - Strategy Pattern Implementation

This module provides a factory for creating the appropriate scraper
based on the source type configuration.
"""

from typing import Type
from loguru import logger

from models import SourceConfig
from .base_scraper import BaseScraper
from .html_scraper import HTMLTableScraper
from .pdf_scraper import PDFScraper
from .dynamic_scraper import DynamicScraper


class ScraperFactory:
    """
    Factory class for creating scrapers based on source type.
    
    Implements the Strategy Pattern to select the appropriate
    scraper implementation at runtime.
    """
    
    # Mapping of source types to scraper classes
    SCRAPER_TYPES: dict[str, Type[BaseScraper]] = {
        'html_table': HTMLTableScraper,
        'pdf': PDFScraper,
        'dynamic': DynamicScraper,
        'unstructured_text': DynamicScraper,  # Can be enhanced with LLM later
    }
    
    @classmethod
    def create_scraper(
        cls,
        source_config: SourceConfig,
        headless: bool = True,
        timeout: int = 30000,
        max_retries: int = 3
    ) -> BaseScraper:
        """
        Create and return the appropriate scraper for the given source.
        
        Args:
            source_config: Configuration for the data source
            headless: Run browser in headless mode
            timeout: Page load timeout in milliseconds
            max_retries: Maximum number of retry attempts
            
        Returns:
            Instantiated scraper object
            
        Raises:
            ValueError: If source type is not supported
        """
        source_type = source_config.type
        
        scraper_class = cls.SCRAPER_TYPES.get(source_type)
        
        if not scraper_class:
            supported_types = ', '.join(cls.SCRAPER_TYPES.keys())
            raise ValueError(
                f"Unsupported source type: {source_type}. "
                f"Supported types: {supported_types}"
            )
        
        logger.info(f"Creating {scraper_class.__name__} for source: {source_config.name}")
        
        return scraper_class(
            source_config=source_config,
            headless=headless,
            timeout=timeout,
            max_retries=max_retries
        )
    
    @classmethod
    def get_supported_types(cls) -> list[str]:
        """
        Get list of supported source types.
        
        Returns:
            List of supported type strings
        """
        return list(cls.SCRAPER_TYPES.keys())
    
    @classmethod
    def register_scraper_type(cls, source_type: str, scraper_class: Type[BaseScraper]) -> None:
        """
        Register a new scraper type (for extensibility).
        
        Args:
            source_type: Type identifier string
            scraper_class: Scraper class to register
        """
        if not issubclass(scraper_class, BaseScraper):
            raise TypeError(f"{scraper_class} must be a subclass of BaseScraper")
        
        cls.SCRAPER_TYPES[source_type] = scraper_class
        logger.info(f"Registered new scraper type: {source_type} -> {scraper_class.__name__}")
