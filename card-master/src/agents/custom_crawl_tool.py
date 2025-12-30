"""
Custom Crawl4ai Tool with optimized configuration for bank websites.

Bank websites often have heavy JavaScript rendering. This tool provides
proper wait strategies and timeouts to handle these sites.
"""

import asyncio
from typing import Optional

try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False


class OptimizedCrawler:
    """
    Optimized web crawler for bank credit card pages.

    Uses proper wait strategies to handle JavaScript-heavy sites.
    """

    def __init__(
        self,
        headless: bool = True,
        timeout: int = 60000,
        delay: float = 5.0,
        max_length: int = 50000,
    ):
        self.headless = headless
        self.timeout = timeout
        self.delay = delay
        self.max_length = max_length

    async def crawl(self, url: str) -> dict:
        """
        Crawl a URL and return structured result.

        Args:
            url: URL to crawl

        Returns:
            Dict with 'success', 'html', 'markdown', 'error' keys
        """
        if not CRAWL4AI_AVAILABLE:
            return {
                'success': False,
                'html': '',
                'markdown': '',
                'error': 'crawl4ai not installed'
            }

        browser_config = BrowserConfig(
            headless=self.headless,
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        )

        run_config = CrawlerRunConfig(
            # Use domcontentloaded instead of networkidle to avoid timeouts
            wait_until='domcontentloaded',
            page_timeout=self.timeout,
            # Wait for JavaScript to render
            delay_before_return_html=self.delay,
        )

        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url=url, config=run_config)

                if result.success:
                    # Truncate content if max_length is set
                    markdown = result.markdown or ''
                    html = result.html or ''

                    if self.max_length:
                        if len(markdown) > self.max_length:
                            markdown = markdown[:self.max_length] + '\n... (content truncated)'
                        if len(html) > self.max_length:
                            html = html[:self.max_length]

                    return {
                        'success': True,
                        'html': html,
                        'markdown': markdown,
                        'error': None,
                    }
                else:
                    return {
                        'success': False,
                        'html': '',
                        'markdown': '',
                        'error': result.error_message,
                    }
        except Exception as e:
            return {
                'success': False,
                'html': '',
                'markdown': '',
                'error': str(e),
            }

    def crawl_sync(self, url: str) -> dict:
        """Synchronous wrapper for crawl()."""
        return asyncio.run(self.crawl(url))


def crawl_url(url: str, delay: float = 5.0) -> dict:
    """
    Convenience function to crawl a URL with optimized settings.

    Args:
        url: URL to crawl
        delay: Seconds to wait for JS rendering

    Returns:
        Dict with crawl results
    """
    crawler = OptimizedCrawler(delay=delay)
    return crawler.crawl_sync(url)


async def discover_card_links(listing_url: str, bank: str = None) -> list[dict]:
    """
    Discover credit card links from a bank's listing page.

    Args:
        listing_url: URL of the bank's credit card listing page
        bank: Bank name (helps with pattern matching)

    Returns:
        List of dicts with 'name' and 'url' keys
    """
    import re
    from urllib.parse import urlparse

    crawler = OptimizedCrawler(delay=5.0, max_length=None)  # Don't truncate
    result = await crawler.crawl(listing_url)

    if not result['success']:
        return []

    html = result['html']
    parsed = urlparse(listing_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    discovered = []

    # Bank-specific patterns
    bank_patterns = {
        'BMO': [
            # Full URLs: https://www.bmo.com/.../bmo-xxx-mastercard/
            r'href=\"(https://www\.bmo\.com/[^\"]*?/bmo-[a-z\-]+(?:-mastercard|-visa)?/?)\"',
            # Relative: /main/personal/credit-cards/.../bmo-xxx/
            r'href=\"(/[^\"]*?/bmo-[a-z\-]+(?:-mastercard|-visa)?/?)\"',
        ],
        'TD': [
            r'href=\"([^\"]*?/credit-cards/[^\"]*?(?:visa|mastercard)[^\"]*?)\"',
        ],
        'RBC': [
            r'href=\"([^\"]*?/credit-cards/[^\"]*?(?:rbc-|visa|mastercard)[^\"]*?)\"',
        ],
        'CIBC': [
            r'href=\"([^\"]*?/credit-cards/[^\"]*?(?:visa|mastercard|aventura|dividend|aeroplan)[^\"]*?)\"',
        ],
        'Scotiabank': [
            r'href=\"([^\"]*?/credit-cards/[^\"]*?(?:visa|mastercard|passport|momentum|scene)[^\"]*?)\"',
        ],
        'AMEX': [
            r'href=\"([^\"]*?/credit-cards/[^\"]*?)\"',
            r'href=\"([^\"]*?/charge-cards/[^\"]*?)\"',
        ],
    }

    # Get patterns for this bank
    patterns = bank_patterns.get(bank, [])

    # Add generic patterns
    patterns.extend([
        r'href=\"([^\"]*?/credit-cards?/[^\"]+(?:mastercard|visa|amex|card)[^\"]*?)\"',
        r'href=\"([^\"]*?(?:mastercard|visa)[^\"]*?)\"[^>]*>([^<]*(?:card|mastercard|visa)[^<]*)<',
    ])

    unique_urls = set()

    for pattern in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        for match in matches:
            # Handle both single URL and (url, name) tuples
            url = match[0] if isinstance(match, tuple) else match

            # Make URL absolute
            if url.startswith('/'):
                url = base_url + url

            # Clean URL
            url = url.split('?')[0].rstrip('/')

            # Skip non-card pages
            skip_patterns = ['apply', 'login', 'sign-in', 'compare', 'all-cards',
                           'help', 'faq', 'contact', '#', 'javascript:', 'debit',
                           'activate', 'payment', 'balance', 'protection', 'insurance',
                           'access-details', 'how-to-choose', 'prepaid', 'report-lost',
                           'lost-stolen', 'click-to-pay', 'apple-pay', 'google-pay',
                           'samsung-pay', '/visa-cards', '/mastercard-cards']
            if any(p in url.lower() for p in skip_patterns):
                continue

            # Must be in credit-cards path
            if '/credit-cards/' not in url.lower() and '/charge-cards/' not in url.lower():
                continue

            # Skip category pages (end with category name only)
            category_endings = ['/cashback', '/travel', '/rewards', '/airmiles',
                              '/low-rate', '/no-fee', '/student', '/affinity']
            if any(url.endswith(cat) for cat in category_endings):
                continue

            # URL must contain card brand or bank name pattern
            url_lower = url.lower()
            has_card_indicator = any(ind in url_lower for ind in [
                'mastercard', 'visa', 'amex', '-card',
                'cobalt', 'platinum', 'gold', 'rewards',
                'cashback', 'airmiles', 'eclipse', 'ascend',
            ])
            if not has_card_indicator:
                continue

            unique_urls.add(url)

    # Normalize URLs (remove /en-ca/ prefix duplicates)
    normalized_urls = {}
    for url in unique_urls:
        # Normalize: remove /en-ca/ to detect duplicates
        norm_key = url.replace('/en-ca/', '/').replace('www.bmo.com/', '')
        if norm_key not in normalized_urls:
            normalized_urls[norm_key] = url
        else:
            # Prefer shorter URL (without en-ca)
            if len(url) < len(normalized_urls[norm_key]):
                normalized_urls[norm_key] = url

    # Convert to list of dicts
    for url in normalized_urls.values():
        # Extract card name from URL
        name = url.split('/')[-1].replace('-', ' ').title()
        discovered.append({'name': name, 'url': url})

    return discovered


def discover_cards_sync(listing_url: str, bank: str = None) -> list[dict]:
    """Synchronous wrapper for discover_card_links()."""
    return asyncio.run(discover_card_links(listing_url, bank))


if __name__ == "__main__":
    # Test crawling
    import sys

    if len(sys.argv) < 2:
        print("Usage: python custom_crawl_tool.py <url>")
        print("       python custom_crawl_tool.py discover <listing_url>")
        sys.exit(1)

    if sys.argv[1] == 'discover':
        url = sys.argv[2] if len(sys.argv) > 2 else 'https://www.bmo.com/main/personal/credit-cards/'
        print(f"Discovering cards from: {url}")
        cards = discover_cards_sync(url)
        print(f"\nFound {len(cards)} cards:")
        for card in cards:
            print(f"  - {card['name']}")
            print(f"    {card['url']}")
    else:
        url = sys.argv[1]
        print(f"Crawling: {url}")
        result = crawl_url(url)
        if result['success']:
            print(f"Success! Markdown length: {len(result['markdown'])}")
            print("\nPreview:")
            print(result['markdown'][:2000])
        else:
            print(f"Failed: {result['error']}")
