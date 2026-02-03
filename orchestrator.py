"""
Orchestrator for managing the scraping pipeline.

This module coordinates the execution of multiple scrapers,
handles parallel execution, and aggregates results.
"""

import asyncio
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from loguru import logger

from models import SourceConfig, ScraperResult, MarketPrice
from scrapers import ScraperFactory
from utils import ConfigLoader, setup_logger


class ScraperOrchestrator:
    """
    Orchestrates the execution of multiple scrapers in parallel.
    
    Features:
    - Parallel scraping of multiple sources
    - Result aggregation
    - Error handling and reporting
    - Progress tracking
    """
    
    def __init__(
        self,
        config_path: str = "config/sources.json",
        headless: bool = True,
        timeout: int = 30000,
        max_retries: int = 3
    ):
        """
        Initialize the orchestrator.
        
        Args:
            config_path: Path to sources configuration file
            headless: Run browsers in headless mode
            timeout: Page load timeout in milliseconds
            max_retries: Maximum retry attempts per source
        """
        self.config_loader = ConfigLoader(config_path)
        self.headless = headless
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.results: List[ScraperResult] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    async def scrape_all_active_sources(self) -> List[ScraperResult]:
        """
        Scrape all active sources in parallel.
        
        Returns:
            List of ScraperResult objects
        """
        logger.info("Starting scraping pipeline for all active sources")
        self.start_time = datetime.now()
        
        # Load active sources
        sources = self.config_loader.get_active_sources()
        
        if not sources:
            logger.warning("No active sources found")
            return []
        
        logger.info(f"Found {len(sources)} active sources")
        
        # Create scraping tasks
        tasks = [self._scrape_source(source) for source in sources]
        
        # Execute in parallel
        self.results = await asyncio.gather(*tasks)
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        # Log summary
        self._log_summary()
        logger.info(f"Scraping pipeline completed in {duration:.2f} seconds")
        
        return self.results
    
    async def scrape_source_by_id(self, source_id: str) -> Optional[ScraperResult]:
        """
        Scrape a single source by its ID.
        
        Args:
            source_id: Unique identifier of the source
            
        Returns:
            ScraperResult or None if source not found
        """
        logger.info(f"Scraping single source: {source_id}")
        
        source = self.config_loader.get_source_by_id(source_id)
        if not source:
            logger.error(f"Source not found: {source_id}")
            return None
        
        return await self._scrape_source(source)
    
    async def scrape_sources_by_country(self, country: str) -> List[ScraperResult]:
        """
        Scrape all sources from a specific country.
        
        Args:
            country: ISO 3166-1 alpha-2 country code
            
        Returns:
            List of ScraperResult objects
        """
        logger.info(f"Scraping sources for country: {country}")
        
        sources = self.config_loader.get_sources_by_country(country)
        
        if not sources:
            logger.warning(f"No sources found for country: {country}")
            return []
        
        tasks = [self._scrape_source(source) for source in sources]
        results = await asyncio.gather(*tasks)
        
        return results
    
    async def _scrape_source(self, source: SourceConfig) -> ScraperResult:
        """
        Scrape a single source using the appropriate scraper.
        
        Args:
            source: SourceConfig object
            
        Returns:
            ScraperResult with prices or error information
        """
        logger.info(f"Scraping source: {source.name} ({source.id})")
        
        try:
            # Create scraper using factory
            scraper = ScraperFactory.create_scraper(
                source_config=source,
                headless=self.headless,
                timeout=self.timeout,
                max_retries=self.max_retries
            )
            
            # Execute scraping with context manager
            async with scraper:
                result = await scraper.scrape()
            
            if result.success:
                logger.info(f"✓ Successfully scraped {result.records_found} records from {source.name}")
            else:
                logger.error(f"✗ Failed to scrape {source.name}: {result.error}")
            
            return result
            
        except Exception as e:
            logger.error(f"✗ Unexpected error scraping {source.name}: {e}")
            return ScraperResult(
                source_id=source.id,
                success=False,
                prices=[],
                error=str(e),
                records_found=0
            )
    
    def _log_summary(self) -> None:
        """Log a summary of scraping results."""
        if not self.results:
            return
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total - successful
        total_records = sum(r.records_found for r in self.results)
        
        logger.info("=" * 60)
        logger.info("SCRAPING SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total sources:      {total}")
        logger.info(f"Successful:         {successful}")
        logger.info(f"Failed:             {failed}")
        logger.info(f"Total records:      {total_records}")
        logger.info("=" * 60)
        
        # Log failed sources
        if failed > 0:
            logger.warning("Failed sources:")
            for result in self.results:
                if not result.success:
                    logger.warning(f"  - {result.source_id}: {result.error}")
    
    def get_all_prices(self) -> List[MarketPrice]:
        """
        Get all successfully scraped prices.
        
        Returns:
            Flattened list of all MarketPrice objects
        """
        all_prices = []
        for result in self.results:
            if result.success:
                all_prices.extend(result.prices)
        return all_prices
    
    def export_results_to_json(self, output_path: str = "output/prices.json") -> None:
        """
        Export all results to JSON file.
        
        Args:
            output_path: Path to output JSON file
        """
        import json
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare data for export
        export_data = {
            'metadata': {
                'scraped_at': datetime.now().isoformat(),
                'total_sources': len(self.results),
                'successful_sources': sum(1 for r in self.results if r.success),
                'total_records': sum(r.records_found for r in self.results)
            },
            'results': [
                {
                    'source_id': result.source_id,
                    'success': result.success,
                    'records_found': result.records_found,
                    'error': result.error,
                    'prices': [price.to_dict() for price in result.prices]
                }
                for result in self.results
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Results exported to: {output_file}")


async def main():
    """
    Main entry point for running the scraper.
    """
    # Setup logging
    setup_logger(log_level="INFO")
    
    logger.info("Starting Agri-Market Scraper Engine")
    
    # Create orchestrator
    orchestrator = ScraperOrchestrator(
        config_path="config/sources.json",
        headless=True,
        timeout=30000,
        max_retries=3
    )
    
    # Scrape all active sources
    results = await orchestrator.scrape_all_active_sources()
    
    # Export results
    orchestrator.export_results_to_json("output/prices.json")
    
    # Get all prices
    all_prices = orchestrator.get_all_prices()
    logger.info(f"Total prices collected: {len(all_prices)}")
    
    logger.info("Scraper engine completed successfully")


if __name__ == "__main__":
    asyncio.run(main())
