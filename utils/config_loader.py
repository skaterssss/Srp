"""
Configuration loader for reading and parsing sources.json
"""

import json
from pathlib import Path
from typing import List, Optional
from loguru import logger

from models import SourceConfig


class ConfigLoader:
    """
    Loader for source configurations from JSON files.
    
    Provides methods to load, filter, and validate source configurations.
    """
    
    def __init__(self, config_path: str = "config/sources.json"):
        """
        Initialize config loader.
        
        Args:
            config_path: Path to sources.json configuration file
        """
        self.config_path = Path(config_path)
        self._sources: Optional[List[SourceConfig]] = None
    
    def load_sources(self, reload: bool = False) -> List[SourceConfig]:
        """
        Load source configurations from JSON file.
        
        Args:
            reload: Force reload even if already cached
            
        Returns:
            List of SourceConfig objects
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If JSON is invalid or validation fails
        """
        if self._sources and not reload:
            return self._sources
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        logger.info(f"Loading source configurations from: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            sources_data = data.get('sources', [])
            
            # Validate and create SourceConfig objects
            sources = []
            for source_data in sources_data:
                try:
                    source_config = SourceConfig(**source_data)
                    sources.append(source_config)
                except Exception as e:
                    logger.error(f"Failed to validate source {source_data.get('id')}: {e}")
                    continue
            
            self._sources = sources
            logger.info(f"Loaded {len(sources)} source configurations")
            
            return sources
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load config: {e}")
    
    def get_source_by_id(self, source_id: str) -> Optional[SourceConfig]:
        """
        Get a specific source configuration by ID.
        
        Args:
            source_id: Unique identifier of the source
            
        Returns:
            SourceConfig object or None if not found
        """
        if not self._sources:
            self.load_sources()
        
        for source in self._sources:
            if source.id == source_id:
                return source
        
        logger.warning(f"Source not found: {source_id}")
        return None
    
    def get_active_sources(self) -> List[SourceConfig]:
        """
        Get only active source configurations.
        
        Returns:
            List of active SourceConfig objects
        """
        if not self._sources:
            self.load_sources()
        
        active = [source for source in self._sources if source.active]
        logger.info(f"Found {len(active)} active sources")
        return active
    
    def get_sources_by_country(self, country: str) -> List[SourceConfig]:
        """
        Filter sources by country code.
        
        Args:
            country: ISO 3166-1 alpha-2 country code (e.g., 'NL', 'DE')
            
        Returns:
            List of matching SourceConfig objects
        """
        if not self._sources:
            self.load_sources()
        
        matches = [source for source in self._sources if source.country.upper() == country.upper()]
        logger.info(f"Found {len(matches)} sources for country {country}")
        return matches
    
    def get_sources_by_type(self, source_type: str) -> List[SourceConfig]:
        """
        Filter sources by type.
        
        Args:
            source_type: Type identifier (html_table, pdf, dynamic, etc.)
            
        Returns:
            List of matching SourceConfig objects
        """
        if not self._sources:
            self.load_sources()
        
        matches = [source for source in self._sources if source.type == source_type]
        logger.info(f"Found {len(matches)} sources of type {source_type}")
        return matches
    
    def validate_all_sources(self) -> dict:
        """
        Validate all source configurations.
        
        Returns:
            Dictionary with validation results
        """
        if not self._sources:
            self.load_sources()
        
        results = {
            'total': len(self._sources),
            'valid': 0,
            'invalid': 0,
            'errors': []
        }
        
        for source in self._sources:
            try:
                # Basic validation checks
                assert source.id, "Source ID is required"
                assert source.name, "Source name is required"
                assert source.url, "Source URL is required"
                assert source.country, "Source country is required"
                assert source.type, "Source type is required"
                
                results['valid'] += 1
            except AssertionError as e:
                results['invalid'] += 1
                results['errors'].append({
                    'source_id': source.id,
                    'error': str(e)
                })
        
        logger.info(f"Validation: {results['valid']} valid, {results['invalid']} invalid")
        return results
