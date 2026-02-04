"""
Dynamic Scraper for JavaScript-heavy websites with AJAX content.

Handles dynamic content loading using Playwright's network interception
and waiting strategies.
"""

from typing import List, Optional, Dict, Any
import asyncio
import json
from datetime import date
from decimal import Decimal

from bs4 import BeautifulSoup
from loguru import logger

from models import MarketPrice, ScraperResult, Commodity, Currency, Unit
from .base_scraper import BaseScraper


class DynamicScraper(BaseScraper):
    """
    Scraper for dynamic websites with JavaScript-rendered content.
    
    Waits for AJAX requests, network idle, or specific elements
    before extracting data.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.intercepted_data: List[Dict[str, Any]] = []
    
    async def scrape(self) -> ScraperResult:
        """
        Scrape dynamic website and extract market prices.
        
        Returns:
            ScraperResult with extracted prices or error information
        """
        try:
            # Set up network interception
            await self._setup_network_interception()
            
            # Get wait configuration
            wait_for = self.source_config.selectors.get('wait_for') if self.source_config.selectors else None
            
            # Fetch content with waiting strategy
            html_content = await self._fetch_dynamic_content(wait_for)
            
            # Try to extract from intercepted API responses first
            prices = []
            if self.intercepted_data:
                prices = await self._extract_from_api_responses()
            
            # Fallback to HTML parsing if no API data
            if not prices:
                prices = await self._extract_from_html(html_content)
            
            logger.info(f"Extracted {len(prices)} prices from dynamic source: {self.source_config.name}")
            return self._create_success_result(prices)
            
        except Exception as e:
            logger.error(f"Error scraping dynamic source {self.source_config.name}: {e}")
            return self._create_error_result(str(e))
    
    async def _setup_network_interception(self) -> None:
        """
        Set up network request/response interception to capture API data.
        """
        if not self.page:
            await self.initialize_browser()
        
        async def handle_response(response):
            """Intercept and store relevant API responses"""
            try:
                url = response.url
                
                # Look for API endpoints with price data
                if any(keyword in url.lower() for keyword in ['price', 'market', 'data', 'api', 'json']):
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        
                        if 'application/json' in content_type:
                            try:
                                data = await response.json()
                                self.intercepted_data.append({
                                    'url': url,
                                    'data': data,
                                    'timestamp': date.today().isoformat()
                                })
                                logger.info(f"Intercepted API response from: {url}")
                            except Exception as e:
                                logger.warning(f"Failed to parse JSON from {url}: {e}")
            except Exception as e:
                logger.warning(f"Error handling response: {e}")
        
        self.page.on('response', handle_response)
    
    async def _fetch_dynamic_content(self, wait_for: Optional[str] = None) -> str:
        """
        Fetch content from dynamic website with proper waiting.
        
        Args:
            wait_for: CSS selector to wait for, or special keywords:
                     - 'networkidle': Wait for network to be idle
                     - 'load': Wait for load event
                     - Otherwise: CSS selector to wait for
        
        Returns:
            Raw HTML content as string
        """
        if not self.page:
            await self.initialize_browser()
        
        logger.info(f"Navigating to: {self.source_config.url}")
        
        # Navigate to page
        if wait_for == 'networkidle':
            await self.page.goto(
                self.source_config.url,
                wait_until='networkidle',
                timeout=self.timeout
            )
        elif wait_for == 'load':
            await self.page.goto(
                self.source_config.url,
                wait_until='load',
                timeout=self.timeout
            )
        else:
            await self.page.goto(
                self.source_config.url,
                wait_until='domcontentloaded',
                timeout=self.timeout
            )
            
            # Wait for specific selector if provided
            if wait_for:
                try:
                    await self.page.wait_for_selector(wait_for, timeout=self.timeout)
                except Exception as e:
                    logger.warning(f"Timeout waiting for selector {wait_for}: {e}")
        
        # Additional wait for dynamic content to load
        await asyncio.sleep(2)
        
        # Scroll to trigger lazy loading
        await self._scroll_page()
        
        # Get final content
        content = await self.page.content()
        return content
    
    async def _scroll_page(self) -> None:
        """
        Scroll page to trigger lazy-loaded content.
        """
        try:
            await self.page.evaluate("""
                async () => {
                    await new Promise((resolve) => {
                        let totalHeight = 0;
                        const distance = 100;
                        const timer = setInterval(() => {
                            const scrollHeight = document.body.scrollHeight;
                            window.scrollBy(0, distance);
                            totalHeight += distance;
                            
                            if(totalHeight >= scrollHeight){
                                clearInterval(timer);
                                resolve();
                            }
                        }, 100);
                    });
                }
            """)
            logger.info("Page scrolled to trigger lazy loading")
        except Exception as e:
            logger.warning(f"Failed to scroll page: {e}")
    
    async def _extract_from_api_responses(self) -> List[MarketPrice]:
        """
        Extract prices from intercepted API responses.
        
        Returns:
            List of MarketPrice objects
        """
        prices = []
        
        for response_data in self.intercepted_data:
            try:
                data = response_data['data']
                
                # Handle different JSON structures
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    # Common patterns: data.items, data.results, data.prices
                    items = (
                        data.get('items') or 
                        data.get('results') or 
                        data.get('prices') or 
                        data.get('data') or
                        [data]
                    )
                else:
                    continue
                
                # Parse each item
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    
                    market_price = self._parse_api_item(item)
                    if market_price:
                        prices.append(market_price)
                        
            except Exception as e:
                logger.warning(f"Failed to extract from API response: {e}")
                continue
        
        return prices
    
    def _parse_api_item(self, item: Dict[str, Any]) -> Optional[MarketPrice]:
        """
        Parse a single item from API response into MarketPrice.
        
        Args:
            item: Dictionary from API response
            
        Returns:
            MarketPrice object or None
        """
        try:
            # Common field mappings
            date_fields = ['date', 'datum', 'timestamp', 'updated', 'publicationDate']
            variety_fields = ['variety', 'name', 'product', 'commodity', 'variëteit']
            price_fields = ['price', 'prijs', 'value', 'amount']
            currency_fields = ['currency', 'valuta']
            unit_fields = ['unit', 'eenheid']
            
            # Extract fields
            price_date = self._extract_field(item, date_fields)
            variety = self._extract_field(item, variety_fields)
            price_value = self._extract_field(item, price_fields)
            currency = self._extract_field(item, currency_fields)
            unit = self._extract_field(item, unit_fields)
            
            if not all([variety, price_value]):
                return None
            
            # Parse date
            if price_date:
                from datetime import datetime
                try:
                    if isinstance(price_date, str):
                        price_date = datetime.fromisoformat(price_date.replace('Z', '+00:00')).date()
                except:
                    price_date = date.today()
            else:
                price_date = date.today()
            
            # Parse price
            if isinstance(price_value, str):
                price_value = float(price_value.replace(',', '.'))
            price_value = float(price_value)
            
            # Determine commodity
            commodity = self._determine_commodity(variety)
            
            # Create MarketPrice
            return MarketPrice(
                date=price_date,
                commodity=commodity,
                variety=str(variety).strip(),
                price=Decimal(str(price_value)),
                currency=self._parse_currency(currency),
                unit=self._parse_unit(unit),
                source_id=self.source_config.id,
                country=self.source_config.country,
                metadata={'source': 'api', 'raw_data': item}
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse API item: {e}")
            return None
    
    def _extract_field(self, item: Dict[str, Any], field_names: List[str]) -> Optional[Any]:
        """
        Extract field from item using multiple possible field names.
        
        Args:
            item: Dictionary to search
            field_names: List of possible field names
            
        Returns:
            Field value or None
        """
        for field_name in field_names:
            if field_name in item:
                return item[field_name]
            # Case-insensitive search
            for key in item.keys():
                if key.lower() == field_name.lower():
                    return item[key]
        return None
    
    async def _extract_from_html(self, html_content: str) -> List[MarketPrice]:
        """
        Fallback: Extract prices from rendered HTML.
        
        Args:
            html_content: Rendered HTML content
            
        Returns:
            List of MarketPrice objects
        """
        prices = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Get table selector from config
            table_selector = self.source_config.selectors.get('table_selector') if self.source_config.selectors else None
            
            if table_selector:
                table = soup.select_one(table_selector)
                if table:
                    # Parse similar to HTMLTableScraper
                    from .html_scraper import HTMLTableScraper
                    html_scraper = HTMLTableScraper(self.source_config)
                    prices = await html_scraper._extract_from_table(table)
        
        except Exception as e:
            logger.warning(f"Failed to extract from HTML: {e}")
        
        return prices
    
    def _determine_commodity(self, variety: str) -> Commodity:
        """Determine commodity from variety name."""
        variety_lower = str(variety).lower()
        
        if any(term in variety_lower for term in ['onion', 'ui', 'oignon', 'zwiebel']):
            return Commodity.ONION
        elif any(term in variety_lower for term in ['carrot', 'wortel', 'carotte']):
            return Commodity.CARROT
        else:
            return Commodity.POTATO
    
    def _parse_currency(self, currency: Optional[Any]) -> Currency:
        """Parse currency from API data."""
        if currency:
            currency_str = str(currency).upper()
            if currency_str in ['EUR', 'EURO']:
                return Currency.EUR
            elif currency_str in ['GBP', 'POUND']:
                return Currency.GBP
            elif currency_str == 'PLN':
                return Currency.PLN
            elif currency_str == 'USD':
                return Currency.USD
        
        # Fallback to country-based
        currency_map = {
            'GB': Currency.GBP,
            'UK': Currency.GBP,
            'PL': Currency.PLN,
        }
        return currency_map.get(self.source_config.country, Currency.EUR)
    
    def _parse_unit(self, unit: Optional[Any]) -> Unit:
        """Parse unit from API data."""
        if unit:
            unit_str = str(unit).lower()
            if 'ton' in unit_str:
                return Unit.TON
            elif '100' in unit_str:
                return Unit.KG_100
            elif 'cwt' in unit_str:
                return Unit.CWT
            elif 'kg' in unit_str:
                return Unit.KG
        
        # Default based on country
        if self.source_config.country in ['GB', 'UK']:
            return Unit.CWT
        else:
            return Unit.KG_100
