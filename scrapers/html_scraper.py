"""
HTML Table Scraper for structured market data.

This scraper handles websites that present pricing data in HTML tables,
using BeautifulSoup and pandas for efficient extraction.
"""

from typing import List, Optional
from datetime import datetime, date
from decimal import Decimal
import re

from bs4 import BeautifulSoup
import pandas as pd
from loguru import logger

from models import MarketPrice, ScraperResult, Commodity, Currency, Unit
from .base_scraper import BaseScraper


class HTMLTableScraper(BaseScraper):
    """
    Scraper for HTML table-based price sources.
    
    Extracts pricing data from standard HTML tables using CSS selectors
    defined in the source configuration.
    """
    
    async def scrape(self) -> ScraperResult:
        """
        Scrape HTML table and extract market prices.
        
        Returns:
            ScraperResult with extracted prices or error information
        """
        try:
            # Fetch page content
            html_content = await self.get_page_content(self.source_config.url)
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract table using configured selector
            table_selector = self.source_config.selectors.get('table_selector')
            if not table_selector:
                return self._create_error_result("No table_selector defined in source config")
            
            table = soup.select_one(table_selector)
            if not table:
                logger.warning(f"Table not found with selector: {table_selector}")
                # Try pandas read_html as fallback
                prices = await self._extract_with_pandas(html_content)
            else:
                prices = await self._extract_from_table(table)
            
            logger.info(f"Extracted {len(prices)} prices from {self.source_config.name}")
            return self._create_success_result(prices)
            
        except Exception as e:
            logger.error(f"Error scraping {self.source_config.name}: {e}")
            return self._create_error_result(str(e))
    
    async def _extract_from_table(self, table) -> List[MarketPrice]:
        """
        Extract prices from a BeautifulSoup table element.
        
        Args:
            table: BeautifulSoup table element
            
        Returns:
            List of MarketPrice objects
        """
        prices = []
        rows = table.find_all('tr')
        
        # Skip header row
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 3:
                continue
            
            try:
                # Extract data based on configured column indices
                price_data = self._parse_row_cells(cells)
                if price_data:
                    market_price = self._create_market_price(price_data)
                    if market_price:
                        prices.append(market_price)
            except Exception as e:
                logger.warning(f"Failed to parse row: {e}")
                continue
        
        return prices
    
    async def _extract_with_pandas(self, html_content: str) -> List[MarketPrice]:
        """
        Extract prices using pandas.read_html as fallback.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            List of MarketPrice objects
        """
        prices = []
        
        try:
            # Read all tables
            dfs = pd.read_html(html_content)
            
            if not dfs:
                return prices
            
            # Use the largest table (likely contains the price data)
            df = max(dfs, key=lambda x: len(x))
            
            # Process each row
            for _, row in df.iterrows():
                try:
                    price_data = self._parse_dataframe_row(row)
                    if price_data:
                        market_price = self._create_market_price(price_data)
                        if market_price:
                            prices.append(market_price)
                except Exception as e:
                    logger.warning(f"Failed to parse dataframe row: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Pandas extraction failed: {e}")
        
        return prices
    
    def _parse_row_cells(self, cells: List) -> Optional[dict]:
        """
        Parse table cells into structured data.
        
        Args:
            cells: List of BeautifulSoup cell elements
            
        Returns:
            Dictionary with parsed data or None
        """
        try:
            # Get column mapping from config
            selectors = self.source_config.selectors or {}
            date_col = selectors.get('date_column', 0)
            variety_col = selectors.get('variety_column', 1)
            price_col = selectors.get('price_column', 2)
            
            # Extract text from cells
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            
            if len(cell_texts) <= max(date_col, variety_col, price_col):
                return None
            
            return {
                'date_str': cell_texts[date_col] if date_col < len(cell_texts) else None,
                'variety': cell_texts[variety_col] if variety_col < len(cell_texts) else None,
                'price_str': cell_texts[price_col] if price_col < len(cell_texts) else None,
            }
        except Exception as e:
            logger.warning(f"Error parsing cells: {e}")
            return None
    
    def _parse_dataframe_row(self, row: pd.Series) -> Optional[dict]:
        """
        Parse pandas Series row into structured data.
        
        Args:
            row: Pandas Series representing a table row
            
        Returns:
            Dictionary with parsed data or None
        """
        try:
            # Try to identify columns by common names
            row_dict = row.to_dict()
            
            # Look for date column
            date_str = None
            for key, value in row_dict.items():
                if any(term in str(key).lower() for term in ['date', 'datum', 'fecha']):
                    date_str = str(value)
                    break
            
            # Look for variety column
            variety = None
            for key, value in row_dict.items():
                if any(term in str(key).lower() for term in ['variety', 'variëteit', 'sorte', 'ras']):
                    variety = str(value)
                    break
            
            # Look for price column
            price_str = None
            for key, value in row_dict.items():
                if any(term in str(key).lower() for term in ['price', 'prijs', 'prix', 'precio']):
                    price_str = str(value)
                    break
            
            # If not found by column names, use positional
            if not all([date_str, variety, price_str]):
                values = list(row_dict.values())
                date_str = str(values[0]) if len(values) > 0 else None
                variety = str(values[1]) if len(values) > 1 else None
                price_str = str(values[2]) if len(values) > 2 else None
            
            return {
                'date_str': date_str,
                'variety': variety,
                'price_str': price_str,
            }
        except Exception as e:
            logger.warning(f"Error parsing dataframe row: {e}")
            return None
    
    def _create_market_price(self, price_data: dict) -> Optional[MarketPrice]:
        """
        Create a MarketPrice object from parsed data.
        
        Args:
            price_data: Dictionary with date_str, variety, price_str
            
        Returns:
            MarketPrice object or None if validation fails
        """
        try:
            # Parse date
            price_date = self._parse_date(price_data.get('date_str'))
            if not price_date:
                return None
            
            # Parse price
            price_value = self._parse_price(price_data.get('price_str'))
            if price_value is None:
                return None
            
            # Determine commodity (default to Potato, can be enhanced)
            commodity = self._determine_commodity(price_data.get('variety', ''))
            
            # Create MarketPrice
            return MarketPrice(
                date=price_date,
                commodity=commodity,
                variety=price_data.get('variety', 'Unknown').strip(),
                price=Decimal(str(price_value)),
                currency=self._determine_currency(),
                unit=self._determine_unit(),
                source_id=self.source_config.id,
                country=self.source_config.country,
                quality_grade=None,
                metadata={}
            )
            
        except Exception as e:
            logger.warning(f"Failed to create MarketPrice: {e}")
            return None
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """
        Parse date string to date object.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            date object or None
        """
        if not date_str:
            # Use today as fallback
            return date.today()
        
        # Try common date formats
        formats = [
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%Y/%m/%d',
            '%d.%m.%Y',
            '%Y.%m.%d',
            '%d %B %Y',
            '%d %b %Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return date.today()
    
    def _parse_price(self, price_str: Optional[str]) -> Optional[float]:
        """
        Parse price string to float.
        
        Args:
            price_str: Price string (e.g., "€12.50", "12,50", "12.50 EUR")
            
        Returns:
            Float price or None
        """
        if not price_str:
            return None
        
        # Remove currency symbols and whitespace
        price_clean = re.sub(r'[€$£\s]', '', price_str)
        
        # Remove currency codes
        price_clean = re.sub(r'(EUR|USD|GBP|PLN)', '', price_clean, flags=re.IGNORECASE)
        
        # Replace comma with dot (European format)
        price_clean = price_clean.replace(',', '.')
        
        # Extract number
        match = re.search(r'\d+\.?\d*', price_clean)
        if match:
            try:
                return float(match.group())
            except ValueError:
                pass
        
        logger.warning(f"Could not parse price: {price_str}")
        return None
    
    def _determine_commodity(self, variety: str) -> Commodity:
        """
        Determine commodity type from variety name.
        
        Args:
            variety: Variety/product name
            
        Returns:
            Commodity enum value
        """
        variety_lower = variety.lower()
        
        if any(term in variety_lower for term in ['onion', 'ui', 'oignon', 'zwiebel']):
            return Commodity.ONION
        elif any(term in variety_lower for term in ['carrot', 'wortel', 'carotte', 'möhre']):
            return Commodity.CARROT
        else:
            # Default to potato
            return Commodity.POTATO
    
    def _determine_currency(self) -> Currency:
        """
        Determine currency based on country.
        
        Returns:
            Currency enum value
        """
        currency_map = {
            'NL': Currency.EUR,
            'BE': Currency.EUR,
            'DE': Currency.EUR,
            'FR': Currency.EUR,
            'PL': Currency.PLN,
            'GB': Currency.GBP,
            'UK': Currency.GBP,
        }
        return currency_map.get(self.source_config.country, Currency.EUR)
    
    def _determine_unit(self) -> Unit:
        """
        Determine unit based on country conventions.
        
        Returns:
            Unit enum value
        """
        if self.source_config.country in ['GB', 'UK']:
            return Unit.CWT  # UK often uses hundredweight
        else:
            return Unit.KG_100  # Most EU countries use 100kg
