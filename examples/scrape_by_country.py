"""
Example: Scrape sources from a specific country
"""

import asyncio
import sys
from orchestrator import ScraperOrchestrator
from utils import setup_logger


async def main():
    # Setup logging
    setup_logger(log_level="INFO")
    
    # Get country from command line or use default
    country = sys.argv[1] if len(sys.argv) > 1 else "NL"
    
    print(f"🌍 Scraping sources from: {country}")
    
    # Create orchestrator
    orchestrator = ScraperOrchestrator()
    
    # Scrape sources from specified country
    results = await orchestrator.scrape_sources_by_country(country)
    
    # Display results
    print(f"\n📊 Results for {country}:")
    print("=" * 60)
    
    for result in results:
        status = "✅" if result.success else "❌"
        print(f"{status} {result.source_id:30s} | {result.records_found:3d} records")
        if not result.success:
            print(f"   Error: {result.error}")
    
    # Export successful results
    if any(r.success for r in results):
        orchestrator.results = results
        orchestrator.export_results_to_json(f"output/prices_{country}.json")
        print(f"\n💾 Results exported to: output/prices_{country}.json")


if __name__ == "__main__":
    asyncio.run(main())
