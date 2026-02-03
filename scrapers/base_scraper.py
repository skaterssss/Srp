"""
Base Scraper Class with Playwright integration, stealth mode, and retry logic.

This module provides the foundation for all scraping operations with:
- Anti-bot detection bypass using playwright-stealth
- User-agent rotation
- Automatic retry logic with exponential backoff
- PDF download capabilities
- Robust error handling
"""

import os
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
import random

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
from fake_useragent import UserAgent
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from loguru import logger

from models import SourceConfig, ScraperResult, MarketPrice


class BaseScraper(ABC):
    """
    Base class for all scrapers with robust anti-bot detection and error handling.
    
    Features:
    - Playwright-based browser automation (headless mode)
    - Stealth plugin to bypass bot detection
    - User-agent rotation
    - Retry logic (3 attempts with exponential backoff)
    - PDF download support
    - Request/response logging
    """
    
    def __init__(
        self,
        source_config: SourceConfig,
        headless: bool = True,
        timeout: int = 30000,
        max_retries: int = 3
    ):
        """
        Initialize the scraper.
        
        Args:
            source_config: Configuration for the data source
            headless: Run browser in headless mode (default: True)
            timeout: Page load timeout in milliseconds (default: 30000)
            max_retries: Maximum number of retry attempts (default: 3)
        """
        self.source_config = source_config
        self.headless = headless
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent_generator = UserAgent()
        
        # Browser state
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
        # Create temp directory for downloads
        self.temp_dir = Path("/tmp/agri_scraper")
        self.temp_dir.mkdir(exist_ok=True)
        
        logger.info(f"Initialized scraper for source: {source_config.name}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_browser()
    
    def _get_random_user_agent(self) -> str:
        """
        Generate a random user agent string.
        
        Returns:
            Random user agent string
        """
        try:
            return self.user_agent_generator.random
        except Exception:
            # Fallback to common user agents if fake-useragent fails
            fallback_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            return random.choice(fallback_agents)
    
    def _get_stealth_args(self) -> List[str]:
        """
        Get browser launch arguments for stealth mode.
        
        Returns:
            List of browser arguments
        """
        return [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--allow-running-insecure-content',
            '--disable-infobars',
            '--window-size=1920,1080'
        ]
    
    async def initialize_browser(self) -> None:
        """
        Initialize Playwright browser with stealth settings.
        """
        logger.info("Initializing Playwright browser...")
        
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser with stealth arguments
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=self._get_stealth_args()
            )
            
            # Create context with randomized user agent and viewport
            user_agent = self._get_random_user_agent()
            context = await self.browser.new_context(
                user_agent=user_agent,
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='Europe/Amsterdam',
                permissions=[],
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
            
            self.page = await context.new_page()
            
            # Apply additional stealth techniques
            await self._apply_stealth_scripts()
            
            logger.info(f"Browser initialized with user agent: {user_agent[:50]}...")
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise
    
    async def _apply_stealth_scripts(self) -> None:
        """
        Apply JavaScript to bypass bot detection.
        """
        if not self.page:
            return
        
        # Override navigator.webdriver
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        # Mock plugins and languages
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        # Mock chrome object
        await self.page.add_init_script("""
            window.chrome = {
                runtime: {}
            };
        """)
        
        # Mock permissions
        await self.page.add_init_script("""
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
    
    async def close_browser(self) -> None:
        """
        Close browser and cleanup resources.
        """
        logger.info("Closing browser...")
        
        if self.page:
            await self.page.close()
            self.page = None
        
        if self.browser:
            await self.browser.close()
            self.browser = None
        
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=10),
        retry=retry_if_exception_type((PlaywrightTimeoutError, ConnectionError)),
        reraise=True
    )
    async def get_page_content(self, url: str, wait_for_selector: Optional[str] = None) -> str:
        """
        Fetch raw HTML content from a URL with retry logic.
        
        Args:
            url: Target URL to scrape
            wait_for_selector: Optional CSS selector to wait for before returning content
            
        Returns:
            Raw HTML content as string
            
        Raises:
            PlaywrightTimeoutError: If page load times out after retries
            ConnectionError: If connection fails after retries
        """
        if not self.page:
            await self.initialize_browser()
        
        logger.info(f"Fetching content from: {url}")
        
        try:
            # Navigate to page
            response = await self.page.goto(
                url,
                wait_until='domcontentloaded',
                timeout=self.timeout
            )
            
            if response and response.status >= 500:
                logger.warning(f"Server error {response.status} from {url}")
                raise ConnectionError(f"HTTP {response.status}")
            
            # Wait for specific selector if provided
            if wait_for_selector:
                await self.page.wait_for_selector(
                    wait_for_selector,
                    timeout=self.timeout
                )
            
            # Additional random delay to appear more human-like
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            # Get page content
            content = await self.page.content()
            logger.info(f"Successfully fetched {len(content)} bytes from {url}")
            
            return content
            
        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout while fetching {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            raise ConnectionError(f"Failed to fetch {url}: {e}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=10),
        retry=retry_if_exception_type((PlaywrightTimeoutError, ConnectionError)),
        reraise=True
    )
    async def download_pdf(self, url: str, filename: Optional[str] = None) -> Path:
        """
        Download a PDF file to local storage.
        
        Args:
            url: URL of the PDF to download
            filename: Optional custom filename (default: auto-generated)
            
        Returns:
            Path to downloaded PDF file
            
        Raises:
            ConnectionError: If download fails after retries
        """
        if not self.page:
            await self.initialize_browser()
        
        logger.info(f"Downloading PDF from: {url}")
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.source_config.id}_{timestamp}.pdf"
        
        output_path = self.temp_dir / filename
        
        try:
            # Navigate and wait for download
            async with self.page.expect_download() as download_info:
                await self.page.goto(url, timeout=self.timeout)
            
            download = await download_info.value
            await download.save_as(output_path)
            
            logger.info(f"PDF downloaded to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to download PDF from {url}: {e}")
            raise ConnectionError(f"PDF download failed: {e}")
    
    @abstractmethod
    async def scrape(self) -> ScraperResult:
        """
        Main scraping method to be implemented by subclasses.
        
        Each scraper type (HTML, PDF, Dynamic) should implement its own logic.
        
        Returns:
            ScraperResult with extracted market prices
        """
        pass
    
    def _create_error_result(self, error_message: str) -> ScraperResult:
        """
        Create a ScraperResult for error cases.
        
        Args:
            error_message: Description of the error
            
        Returns:
            ScraperResult with error information
        """
        return ScraperResult(
            source_id=self.source_config.id,
            success=False,
            prices=[],
            error=error_message,
            records_found=0
        )
    
    def _create_success_result(self, prices: List[MarketPrice]) -> ScraperResult:
        """
        Create a ScraperResult for successful scraping.
        
        Args:
            prices: List of extracted market prices
            
        Returns:
            ScraperResult with price data
        """
        return ScraperResult(
            source_id=self.source_config.id,
            success=True,
            prices=prices,
            error=None,
            records_found=len(prices)
        )
