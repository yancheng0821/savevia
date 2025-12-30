"""
Bank Credit Card Scraper - Discovers and scrapes credit card pages from bank websites.

This module provides tools to:
1. Search for a bank's credit card listing page
2. Discover individual credit card URLs
3. Scrape credit card detail pages
4. Extract text content for LLM analysis
"""

import asyncio
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin, urlparse

# Try to import playwright, but don't fail if not available
try:
    from playwright.async_api import async_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Try to import crawl4ai as alternative
try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False


@dataclass
class ScrapedPage:
    """Result of scraping a page."""
    url: str
    title: str
    text_content: str
    card_links: list[dict]  # List of {name, url} for discovered card links
    raw_html: Optional[str] = None


@dataclass
class DiscoveredCard:
    """A credit card discovered from bank website."""
    bank: str
    name: str
    url: str
    description: Optional[str] = None


class BankScraper:
    """
    Scraper for discovering and extracting credit card information from bank websites.

    Usage:
        scraper = BankScraper()

        # Discover cards from a bank's credit card listing page
        cards = await scraper.discover_cards_from_listing(
            "https://www.bmo.com/main/personal/credit-cards/",
            bank="BMO"
        )

        # Scrape a specific card page
        page_content = await scraper.scrape_card_page(
            "https://www.bmo.com/main/personal/credit-cards/bmo-cashback-mastercard/"
        )
    """

    # Known bank credit card listing URLs
    BANK_CARD_LISTINGS = {
        "BMO": "https://www.bmo.com/main/personal/credit-cards/",
        "TD": "https://www.td.com/ca/en/personal-banking/products/credit-cards",
        "RBC": "https://www.rbcroyalbank.com/credit-cards/",
        "CIBC": "https://www.cibc.com/en/personal-banking/credit-cards.html",
        "Scotiabank": "https://www.scotiabank.com/ca/en/personal/credit-cards.html",
        "AMEX": "https://www.americanexpress.com/ca/en/credit-cards/all-cards/",
        "Tangerine": "https://www.tangerine.ca/en/products/spending/creditcard",
        "Simplii": "https://www.simplii.com/en/credit-cards.html",
        "Rogers": "https://www.rogersbank.com/en/credit_cards",
        "Desjardins": "https://www.desjardins.com/en/credit-cards.html",
        "HSBC": "https://www.hsbc.ca/credit-cards/",
        "National Bank": "https://www.nbc.ca/personal/credit-cards.html",
    }

    def __init__(self):
        self._browser: Optional[Browser] = None

    async def _get_browser(self):
        """Get or create browser instance."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed. Run: pip install playwright && playwright install")

        if self._browser is None:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(headless=True)
        return self._browser

    async def close(self):
        """Close browser instance."""
        if self._browser:
            await self._browser.close()
            self._browser = None

    def get_bank_listing_url(self, bank: str) -> Optional[str]:
        """Get the credit card listing URL for a bank."""
        bank_upper = bank.upper()
        for key, url in self.BANK_CARD_LISTINGS.items():
            if key.upper() == bank_upper or bank_upper in key.upper():
                return url
        return None

    async def scrape_page(self, url: str, wait_time: int = 3000) -> ScrapedPage:
        """
        Scrape a page and extract text content.

        Args:
            url: URL to scrape
            wait_time: Time to wait for page to load (ms)

        Returns:
            ScrapedPage with extracted content
        """
        browser = await self._get_browser()
        page = await browser.new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(wait_time)

            # Get page title
            title = await page.title()

            # Extract all text content
            text_content = await page.evaluate("""
                () => {
                    // Remove script and style elements
                    const scripts = document.querySelectorAll('script, style, noscript');
                    scripts.forEach(el => el.remove());

                    // Get main content areas
                    const main = document.querySelector('main') || document.body;
                    return main.innerText;
                }
            """)

            # Find credit card links
            card_links = await self._extract_card_links(page, url)

            return ScrapedPage(
                url=url,
                title=title,
                text_content=text_content,
                card_links=card_links
            )

        finally:
            await page.close()

    async def _extract_card_links(self, page: Page, base_url: str) -> list[dict]:
        """Extract credit card related links from a page."""
        links = await page.evaluate("""
            () => {
                const links = [];
                const anchors = document.querySelectorAll('a[href]');

                for (const a of anchors) {
                    const href = a.href;
                    const text = a.innerText.trim();

                    // Filter for credit card related links
                    if (href && text && (
                        href.includes('credit-card') ||
                        href.includes('creditcard') ||
                        href.includes('card') ||
                        text.toLowerCase().includes('card') ||
                        text.toLowerCase().includes('mastercard') ||
                        text.toLowerCase().includes('visa')
                    )) {
                        // Skip navigation, footer, apply links
                        if (!href.includes('apply') &&
                            !href.includes('login') &&
                            !href.includes('sign-in') &&
                            !href.includes('#') &&
                            text.length > 3 &&
                            text.length < 100) {
                            links.push({
                                name: text,
                                url: href
                            });
                        }
                    }
                }

                // Remove duplicates
                const seen = new Set();
                return links.filter(link => {
                    if (seen.has(link.url)) return false;
                    seen.add(link.url);
                    return true;
                });
            }
        """)

        return links

    async def discover_cards_from_listing(self, listing_url: str, bank: str) -> list[DiscoveredCard]:
        """
        Discover credit cards from a bank's card listing page.

        Args:
            listing_url: URL of the bank's credit card listing page
            bank: Bank name

        Returns:
            List of discovered credit cards
        """
        page = await self.scrape_page(listing_url)

        discovered = []
        for link in page.card_links:
            # Filter out non-card pages
            url = link["url"]
            name = link["name"]

            # Skip if it looks like a category or general page
            if any(skip in url.lower() for skip in [
                "compare", "all-cards", "help", "faq", "contact",
                "security", "activate", "balance", "payment"
            ]):
                continue

            # Skip if name is too generic
            if name.lower() in ["credit cards", "learn more", "view all", "see all"]:
                continue

            discovered.append(DiscoveredCard(
                bank=bank,
                name=name,
                url=url
            ))

        return discovered

    async def discover_cards_for_bank(self, bank: str) -> list[DiscoveredCard]:
        """
        Discover all credit cards for a specific bank.

        Args:
            bank: Bank name (e.g., "BMO", "TD", "CIBC")

        Returns:
            List of discovered credit cards
        """
        listing_url = self.get_bank_listing_url(bank)
        if not listing_url:
            raise ValueError(f"Unknown bank: {bank}. Known banks: {list(self.BANK_CARD_LISTINGS.keys())}")

        return await self.discover_cards_from_listing(listing_url, bank)

    async def scrape_card_page(self, url: str) -> ScrapedPage:
        """
        Scrape a credit card detail page.

        Args:
            url: URL of the credit card page

        Returns:
            ScrapedPage with extracted content for LLM analysis
        """
        return await self.scrape_page(url, wait_time=5000)


# Convenience functions for sync usage
def discover_cards(bank: str) -> list[DiscoveredCard]:
    """Synchronously discover cards for a bank."""
    async def _run():
        scraper = BankScraper()
        try:
            return await scraper.discover_cards_for_bank(bank)
        finally:
            await scraper.close()

    return asyncio.run(_run())


def scrape_card(url: str) -> ScrapedPage:
    """Synchronously scrape a card page."""
    async def _run():
        scraper = BankScraper()
        try:
            return await scraper.scrape_card_page(url)
        finally:
            await scraper.close()

    return asyncio.run(_run())


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m src.agents.bank_scraper discover <bank>")
        print("  python -m src.agents.bank_scraper scrape <url>")
        print("")
        print("Examples:")
        print("  python -m src.agents.bank_scraper discover BMO")
        print("  python -m src.agents.bank_scraper scrape https://www.bmo.com/...")
        sys.exit(1)

    command = sys.argv[1]

    if command == "discover":
        if len(sys.argv) < 3:
            print("Error: Please provide bank name")
            sys.exit(1)
        bank = sys.argv[2]
        print(f"Discovering cards for {bank}...")
        cards = discover_cards(bank)
        print(f"\nFound {len(cards)} cards:")
        for card in cards:
            print(f"  - {card.name}")
            print(f"    URL: {card.url}")

    elif command == "scrape":
        if len(sys.argv) < 3:
            print("Error: Please provide URL")
            sys.exit(1)
        url = sys.argv[2]
        print(f"Scraping {url}...")
        page = scrape_card(url)
        print(f"\nTitle: {page.title}")
        print(f"\nContent preview (first 2000 chars):")
        print(page.text_content[:2000])

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
