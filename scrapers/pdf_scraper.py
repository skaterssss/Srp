"""
PDF Scraper for extracting market data from PDF documents.

Handles PDF downloads and table extraction using pdfplumber and PyPDF2.
"""

from typing import List, Optional
from pathlib import Path
from datetime import date
from decimal import Decimal
import re

import pdfplumber
import PyPDF2
from loguru import logger

from models import MarketPrice, ScraperResult, Commodity, Currency, Unit
from .base_scraper import BaseScraper


class PDFScraper(BaseScraper):
    """
    Scraper for PDF-based price reports.
    
    Downloads PDFs and extracts pricing tables using pdfplumber for
    structured data extraction.
    """
    
    async def scrape(self) -> ScraperResult:
        """
        Download PDF and extract market prices.
        
        Returns:
            ScraperResult with extracted prices or error information
        """
        try:
            # Get PDF config
            pdf_config = self.source_config.pdf_config
            if not pdf_config:
                return self._create_error_result("No pdf_config defined in source config")
            
            download_url = pdf_config.get('download_url', self.source_config.url)
            
            # Download PDF
            pdf_path = await self.download_pdf(download_url)
            
            # Extract prices based on method
            extraction_method = pdf_config.get('extraction_method', 'table')
            if extraction_method == 'table':
                prices = await self._extract_tables(pdf_path)
            else:
                prices = await self._extract_text(pdf_path)
            
            logger.info(f"Extracted {len(prices)} prices from PDF: {self.source_config.name}")
            return self._create_success_result(prices)
            
        except Exception as e:
            logger.error(f"Error scraping PDF {self.source_config.name}: {e}")
            return self._create_error_result(str(e))
    
    async def _extract_tables(self, pdf_path: Path) -> List[MarketPrice]:
        """
        Extract prices from PDF tables using pdfplumber.
        
        Args:
            pdf_path: Path to downloaded PDF file
            
        Returns:
            List of MarketPrice objects
        """
        prices = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    logger.info(f"Processing page {page_num + 1}/{len(pdf.pages)}")
                    
                    # Extract tables from page
                    tables = page.extract_tables()
                    
                    for table in tables:
                        if not table or len(table) < 2:
                            continue
                        
                        # Process table rows (skip header)
                        for row in table[1:]:
                            try:
                                price_data = self._parse_pdf_row(row)
                                if price_data:
                                    market_price = self._create_market_price(price_data)
                                    if market_price:
                                        prices.append(market_price)
                            except Exception as e:
                                logger.warning(f"Failed to parse PDF row: {e}")
                                continue
        
        except Exception as e:
            logger.error(f"Failed to extract tables from PDF: {e}")
        
        return prices
    
    async def _extract_text(self, pdf_path: Path) -> List[MarketPrice]:
        """
        Extract prices from unstructured PDF text using pattern matching.
        
        Args:
            pdf_path: Path to downloaded PDF file
            
        Returns:
            List of MarketPrice objects
        """
        prices = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # Look for price patterns
                    # Example: "Agria: €12.50/100kg" or "Fontane 15.30 EUR/100kg"
                    pattern = r'([A-Za-z\s]+)[:\s]+([€$£]?\s*\d+[.,]\d{2})\s*([A-Z]{3})?[/\s]*(kg|100kg|ton)?'
                    matches = re.finditer(pattern, text)
                    
                    for match in matches:
                        try:
                            variety = match.group(1).strip()
                            price_str = match.group(2)
                            currency_str = match.group(3)
                            unit_str = match.group(4)
                            
                            price_data = {
                                'variety': variety,
                                'price_str': price_str,
                                'currency': currency_str,
                                'unit': unit_str
                            }
                            
                            market_price = self._create_market_price(price_data)
                            if market_price:
                                prices.append(market_price)
                        except Exception as e:
                            logger.warning(f"Failed to parse text match: {e}")
                            continue
        
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
        
        return prices
    
    def _parse_pdf_row(self, row: List[Optional[str]]) -> Optional[dict]:
        """
        Parse a PDF table row into structured data.
        
        Args:
            row: List of cell values from PDF table
            
        Returns:
            Dictionary with parsed data or None
        """
        try:
            # Filter out None values
            cells = [str(cell).strip() if cell else '' for cell in row]
            
            # Remove empty cells
            cells = [cell for cell in cells if cell]
            
            if len(cells) < 2:
                return None
            
            # Heuristic: First cell is usually variety, last cell is price
            return {
                'variety': cells[0],
                'price_str': cells[-1],
                'date_str': cells[1] if len(cells) > 2 else None
            }
            
        except Exception as e:
            logger.warning(f"Error parsing PDF row: {e}")
            return None
    
    def _create_market_price(self, price_data: dict) -> Optional[MarketPrice]:
        """
        Create a MarketPrice object from parsed PDF data.
        
        Args:
            price_data: Dictionary with variety, price_str, etc.
            
        Returns:
            MarketPrice object or None if validation fails
        """
        try:
            # Parse price
            price_value = self._parse_price(price_data.get('price_str'))
            if price_value is None:
                return None
            
            # Determine commodity
            commodity = self._determine_commodity(price_data.get('variety', ''))
            
            # Parse date if available
            price_date = date.today()  # Default to today for PDFs
            if price_data.get('date_str'):
                parsed_date = self._parse_date(price_data['date_str'])
                if parsed_date:
                    price_date = parsed_date
            
            # Create MarketPrice
            return MarketPrice(
                date=price_date,
                commodity=commodity,
                variety=price_data.get('variety', 'Unknown').strip(),
                price=Decimal(str(price_value)),
                currency=self._determine_currency(price_data.get('currency')),
                unit=self._determine_unit(price_data.get('unit')),
                source_id=self.source_config.id,
                country=self.source_config.country,
                quality_grade=None,
                metadata={'source_type': 'pdf'}
            )
            
        except Exception as e:
            logger.warning(f"Failed to create MarketPrice from PDF: {e}")
            return None
    
    def _parse_price(self, price_str: Optional[str]) -> Optional[float]:
        """Parse price string to float."""
        if not price_str:
            return None
        
        # Remove currency symbols
        price_clean = re.sub(r'[€$£\s]', '', price_str)
        price_clean = re.sub(r'(EUR|USD|GBP|PLN)', '', price_clean, flags=re.IGNORECASE)
        price_clean = price_clean.replace(',', '.')
        
        match = re.search(r'\d+\.?\d*', price_clean)
        if match:
            try:
                return float(match.group())
            except ValueError:
                pass
        
        return None
    
    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string."""
        from datetime import datetime
        
        formats = ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%d.%m.%Y']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue
        
        return None
    
    def _determine_commodity(self, variety: str) -> Commodity:
        """Determine commodity from variety name."""
        variety_lower = variety.lower()
        
        if any(term in variety_lower for term in ['onion', 'ui', 'oignon']):
            return Commodity.ONION
        elif any(term in variety_lower for term in ['carrot', 'wortel', 'carotte']):
            return Commodity.CARROT
        else:
            return Commodity.POTATO
    
    def _determine_currency(self, currency_str: Optional[str]) -> Currency:
        """Determine currency from string or country."""
        if currency_str:
            currency_upper = currency_str.upper()
            if currency_upper in ['EUR', 'EURO']:
                return Currency.EUR
            elif currency_upper in ['GBP', 'POUND']:
                return Currency.GBP
            elif currency_upper == 'PLN':
                return Currency.PLN
            elif currency_upper == 'USD':
                return Currency.USD
        
        # Fallback to country-based mapping
        currency_map = {
            'GB': Currency.GBP,
            'UK': Currency.GBP,
            'PL': Currency.PLN,
        }
        return currency_map.get(self.source_config.country, Currency.EUR)
    
    def _determine_unit(self, unit_str: Optional[str]) -> Unit:
        """Determine unit from string or country."""
        if unit_str:
            unit_lower = unit_str.lower()
            if 'ton' in unit_lower:
                return Unit.TON
            elif '100' in unit_lower or 'hundred' in unit_lower:
                return Unit.KG_100
            elif 'cwt' in unit_lower:
                return Unit.CWT
            elif 'kg' in unit_lower:
                return Unit.KG
        
        # Default based on country
        if self.source_config.country in ['GB', 'UK']:
            return Unit.CWT
        else:
            return Unit.KG_100
