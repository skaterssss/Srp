"""
Example: Validate source configurations without scraping
"""

from utils import ConfigLoader, setup_logger


def main():
    # Setup logging
    setup_logger(log_level="INFO")
    
    print("🔍 Validating source configurations...\n")
    
    # Load config
    config_loader = ConfigLoader("config/sources.json")
    
    try:
        sources = config_loader.load_sources()
        
        print(f"✅ Successfully loaded {len(sources)} sources\n")
        
        # Show summary by country
        countries = {}
        for source in sources:
            countries[source.country] = countries.get(source.country, 0) + 1
        
        print("📊 Sources by country:")
        for country, count in sorted(countries.items()):
            print(f"  {country}: {count} source(s)")
        
        # Show summary by type
        types = {}
        for source in sources:
            types[source.type] = types.get(source.type, 0) + 1
        
        print("\n📊 Sources by type:")
        for source_type, count in sorted(types.items()):
            print(f"  {source_type}: {count} source(s)")
        
        # Show active vs inactive
        active_count = sum(1 for s in sources if s.active)
        inactive_count = len(sources) - active_count
        
        print(f"\n📊 Status:")
        print(f"  Active: {active_count}")
        print(f"  Inactive: {inactive_count}")
        
        # Validate all
        validation_results = config_loader.validate_all_sources()
        
        print(f"\n✅ Validation complete:")
        print(f"  Valid: {validation_results['valid']}")
        print(f"  Invalid: {validation_results['invalid']}")
        
        if validation_results['errors']:
            print("\n❌ Validation errors:")
            for error in validation_results['errors']:
                print(f"  - {error['source_id']}: {error['error']}")
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
