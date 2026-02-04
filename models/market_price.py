"""
Pydantic models for market price data validation and normalization.

This module defines the output schema for scraped agricultural market data,
ensuring type safety and data consistency across the pipeline.
"""

from datetime import date
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from decimal import Decimal


class Commodity(str, Enum):
    """Supported agricultural commodities"""
    POTATO = "Potato"
    ONION = "Onion"
    CARROT = "Carrot"


class Currency(str, Enum):
    """Supported currencies (will be normalized to EUR in Transform layer)"""
    EUR = "EUR"
    PLN = "PLN"
    GBP = "GBP"
    USD = "USD"


class Unit(str, Enum):
    """Supported weight units (will be normalized to kg in Transform layer)"""
    KG = "kg"
    KG_100 = "100kg"
    TON = "ton"
    LB = "lb"  # pound (for UK sources)
    CWT = "cwt"  # hundredweight


class QualityGrade(str, Enum):
    """Common quality classifications"""
    CLASS_I = "Class I"
    CLASS_II = "Class II"
    EXTRA = "Extra"
    FRITESGESCHIKT = "Fritesgeschikt"  # Dutch: suitable for fries
    INDUSTRIAL = "Industrial"
    ORGANIC = "Organic"
    CONVENTIONAL = "Conventional"


class MarketPrice(BaseModel):
    """
    Validated output schema for agricultural market prices.
    
    This model represents a single price observation from a market source.
    All fields are validated for type safety and business logic constraints.
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    date: date = Field(
        ...,
        description="Date of the price observation (YYYY-MM-DD)"
    )
    
    commodity: Commodity = Field(
        ...,
        description="Type of agricultural product"
    )
    
    variety: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Specific variety or cultivar (e.g., 'Agria', 'Fontane', 'Red Onion')"
    )
    
    price: Decimal = Field(
        ...,
        ge=0,
        description="Price value (must be non-negative, max 2 decimal places)"
    )
    
    currency: Currency = Field(
        ...,
        description="Currency of the price"
    )
    
    unit: Unit = Field(
        ...,
        description="Unit of measurement for the price"
    )
    
    source_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Identifier of the source from sources.json"
    )
    
    quality_grade: Optional[str] = Field(
        None,
        max_length=50,
        description="Quality classification (e.g., 'Class I', 'Fritesgeschikt')"
    )
    
    country: str = Field(
        ...,
        min_length=2,
        max_length=2,
        description="ISO 3166-1 alpha-2 country code"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata from the source"
    )
    
    @field_validator('date')
    @classmethod
    def validate_date_not_future(cls, v: date) -> date:
        """Ensure date is not in the future"""
        from datetime import date as date_type
        today = date_type.today()
        if v > today:
            raise ValueError(f"Date cannot be in the future: {v}")
        return v
    
    @field_validator('variety')
    @classmethod
    def normalize_variety(cls, v: str) -> str:
        """Normalize variety names"""
        return v.strip().title()
    
    @field_validator('country')
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        """Ensure country code is uppercase"""
        return v.upper()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary with enums as strings"""
        return self.model_dump(mode='json')
    
    def normalize_to_eur_per_kg(self, exchange_rates: Dict[str, Decimal]) -> Decimal:
        """
        Normalize price to EUR per kg for comparison.
        
        Args:
            exchange_rates: Dictionary mapping currency codes to EUR rates
            
        Returns:
            Normalized price in EUR per kg
        """
        # Convert to EUR
        if self.currency == Currency.EUR:
            price_eur = self.price
        else:
            rate = exchange_rates.get(self.currency.value)
            if rate is None:
                raise ValueError(f"No exchange rate found for {self.currency}")
            price_eur = self.price * rate
        
        # Convert to per kg
        if self.unit == Unit.KG:
            return price_eur
        elif self.unit == Unit.KG_100:
            return price_eur / Decimal("100")
        elif self.unit == Unit.TON:
            return price_eur / Decimal("1000")
        elif self.unit == Unit.LB:
            return price_eur / Decimal("0.453592")  # 1 lb = 0.453592 kg
        elif self.unit == Unit.CWT:
            return price_eur / Decimal("50.8023")  # 1 cwt = 50.8023 kg
        else:
            raise ValueError(f"Unknown unit: {self.unit}")


class SourceConfig(BaseModel):
    """
    Configuration model for a data source from sources.json
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    id: str = Field(..., description="Unique identifier for the source")
    name: str = Field(..., description="Human-readable name")
    url: str = Field(..., description="Base URL of the source")
    country: str = Field(..., min_length=2, max_length=2)
    type: str = Field(..., description="Type: html_table, pdf, unstructured_text, dynamic")
    frequency: str = Field(..., description="Update frequency: daily, weekly")
    active: bool = Field(default=True, description="Whether to scrape this source")
    selectors: Optional[Dict[str, Any]] = Field(default=None, description="CSS/XPath selectors")
    pdf_config: Optional[Dict[str, Any]] = Field(default=None, description="PDF extraction config")
    llm_config: Optional[Dict[str, Any]] = Field(default=None, description="LLM extraction config")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate source type"""
        valid_types = ['html_table', 'pdf', 'unstructured_text', 'dynamic']
        if v not in valid_types:
            raise ValueError(f"Invalid type. Must be one of: {valid_types}")
        return v
    
    @field_validator('frequency')
    @classmethod
    def validate_frequency(cls, v: str) -> str:
        """Validate update frequency"""
        valid_frequencies = ['daily', 'weekly', 'monthly']
        if v not in valid_frequencies:
            raise ValueError(f"Invalid frequency. Must be one of: {valid_frequencies}")
        return v


class ScraperResult(BaseModel):
    """
    Result of a scraping operation
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    source_id: str
    success: bool
    prices: List[MarketPrice] = Field(default_factory=list)
    error: Optional[str] = None
    timestamp: date = Field(default_factory=date.today)
    records_found: int = 0
    
    def __init__(self, **data):
        super().__init__(**data)
        if 'records_found' not in data:
            self.records_found = len(self.prices)
