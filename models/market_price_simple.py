"""
Simplified Pydantic models that work reliably
"""

from datetime import date
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class Commodity(str, Enum):
    """Supported agricultural commodities"""
    POTATO = "Potato"
    ONION = "Onion"
    CARROT = "Carrot"


class Currency(str, Enum):
    """Supported currencies"""
    EUR = "EUR"
    PLN = "PLN"
    GBP = "GBP"
    USD = "USD"


class Unit(str, Enum):
    """Supported weight units"""
    KG = "kg"
    KG_100 = "100kg"
    TON = "ton"
    LB = "lb"
    CWT = "cwt"


class MarketPrice(BaseModel):
    """Simplified market price model"""
    
    date: date
    commodity: Commodity
    variety: str
    price: float
    currency: Currency
    unit: Unit
    source_id: str
    country: str
    quality_grade: Optional[str] = None


class SourceConfig(BaseModel):
    """Source configuration"""
    
    id: str
    name: str
    url: str
    country: str
    type: str
    frequency: str
    active: bool = True
    selectors: Optional[dict] = None
    pdf_config: Optional[dict] = None
    llm_config: Optional[dict] = None


class ScraperResult(BaseModel):
    """Scraping result"""
    
    source_id: str
    success: bool
    prices: List[MarketPrice] = []
    error: Optional[str] = None
    records_found: int = 0
