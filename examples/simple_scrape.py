"""
Simple example: Scrape all active sources and export to JSON
"""

import asyncio
from orchestrator import ScraperOrchestrator
from utils import setup_logger


async def main():
    # Setup logging
    setup_logger(log_level="INFO")
    
    # Create orchestrator
    orchestrator = ScraperOrchestrator(
        config_path="config/sources.json",
        headless=True,
        timeout=30000,
        max_retries=3
    )
    
    # Scrape all active sources
    print("🌾 Starting scraping pipeline...")
    results = await orchestrator.scrape_all_active_sources()
    
    # Export to JSON
    orchestrator.export_results_to_json("output/prices.json")
    
    # Display results
    all_prices = orchestrator.get_all_prices()
    print(f"\n✅ Scraping complete!")
    print(f"📊 Total prices collected: {len(all_prices)}")
    
    # Show sample prices
    if all_prices:
        print("\n🔍 Sample prices:")
        for price in all_prices[:5]:
            print(f"  {price.date} | {price.variety:20s} | €{price.price:6.2f}/{price.unit.value:5s} | {price.country}")


if __name__ == "__main__":
    asyncio.run(main())
