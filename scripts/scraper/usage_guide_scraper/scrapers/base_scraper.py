"""
Base scraper class with common functionality
"""

import time
import functools
from typing import Optional, List, Callable
from abc import ABC, abstractmethod

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Warning: Selenium not installed. Run: pip install selenium")

import requests
from bs4 import BeautifulSoup

from ..config import REQUEST_HEADERS, REQUEST_TIMEOUT, REQUEST_DELAY
from ..models import ScrapedCardData


def retry(max_attempts: int = 3, delay: float = 2.0):
    """Decorator for retrying failed requests"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


class BaseScraper(ABC):
    """Base class for all scrapers"""

    def __init__(self, use_selenium: bool = True):
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.driver = None
        self.last_request_time = 0

    def init_driver(self):
        """Initialize Selenium WebDriver"""
        if not SELENIUM_AVAILABLE:
            print("Selenium not available, using requests fallback")
            return

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'user-agent={REQUEST_HEADERS["User-Agent"]}')

        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(REQUEST_TIMEOUT)
        except WebDriverException as e:
            print(f"Failed to initialize Chrome driver: {e}")
            self.use_selenium = False

    def close_driver(self):
        """Close WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    def _rate_limit(self):
        """Ensure minimum delay between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < REQUEST_DELAY:
            time.sleep(REQUEST_DELAY - elapsed)
        self.last_request_time = time.time()

    @retry(max_attempts=3, delay=2.0)
    def get_page(self, url: str, wait_selector: str = None, wait_time: int = 2) -> Optional[str]:
        """Get page content with rate limiting and retry

        Args:
            url: URL to fetch
            wait_selector: CSS selector to wait for (Selenium only)
            wait_time: Additional wait time for dynamic content (seconds)
        """
        self._rate_limit()

        if self.use_selenium and self.driver:
            try:
                self.driver.get(url)
                if wait_selector:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
                    )
                # Additional wait for JavaScript content to render
                time.sleep(wait_time)
                return self.driver.page_source
            except TimeoutException:
                print(f"Timeout loading {url}")
                return None
        else:
            try:
                response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                print(f"Request failed for {url}: {e}")
                return None

    def get_soup(self, url: str, wait_selector: str = None, wait_time: int = 2) -> Optional[BeautifulSoup]:
        """Get BeautifulSoup object for a URL

        Args:
            url: URL to fetch
            wait_selector: CSS selector to wait for (Selenium only)
            wait_time: Additional wait time for dynamic content (seconds)
        """
        html = self.get_page(url, wait_selector, wait_time)
        if html:
            return BeautifulSoup(html, 'lxml')
        return None

    @abstractmethod
    def scrape_card(self, card_id: int, card_name: str, bank: str,
                    apply_url: Optional[str] = None) -> Optional[ScrapedCardData]:
        """Scrape usage data for a specific card"""
        raise NotImplementedError

    @abstractmethod
    def scrape_all(self, cards: List[dict]) -> List[ScrapedCardData]:
        """Scrape usage data for all provided cards"""
        raise NotImplementedError

    def __enter__(self):
        if self.use_selenium:
            self.init_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_driver()
