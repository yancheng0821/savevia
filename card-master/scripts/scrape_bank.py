#!/usr/bin/env python3
"""
Bank Credit Card Scraper - Discovers and scrapes credit cards from bank websites.

Usage:
    python scripts/scrape_bank.py discover <bank>     # Discover all cards for a bank
    python scripts/scrape_bank.py scrape <url>        # Scrape a specific card page
    python scripts/scrape_bank.py list-banks          # List all supported banks

Examples:
    python scripts/scrape_bank.py discover BMO
    python scripts/scrape_bank.py scrape https://www.bmo.com/main/personal/credit-cards/bmo-air-miles-world-elite-mastercard/
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.bank_scraper import BankScraper, PLAYWRIGHT_AVAILABLE
from src.agents.card_analyzer import create_analysis_prompt
from src.services.database import Database


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║     Credit Card Scraper - 信用卡优惠信息采集工具                  ║
║     Discover and extract credit card rewards from bank websites  ║
╚══════════════════════════════════════════════════════════════════╝
    """)


async def discover_cards(bank: str):
    """Discover all credit cards for a bank"""
    print(f"\n🔍 Discovering credit cards for: {bank}")
    print("=" * 60)

    scraper = BankScraper()

    # Get listing URL
    listing_url = scraper.get_bank_listing_url(bank)
    if not listing_url:
        print(f"\n❌ Unknown bank: {bank}")
        print(f"\nSupported banks: {list(scraper.BANK_CARD_LISTINGS.keys())}")
        return

    print(f"📍 Listing page: {listing_url}\n")

    try:
        cards = await scraper.discover_cards_for_bank(bank)

        print(f"\n✅ Found {len(cards)} credit cards:\n")
        for i, card in enumerate(cards, 1):
            print(f"  [{i}] {card.name}")
            print(f"      URL: {card.url}\n")

        # Save to database
        db = Database()
        for card in cards:
            db.save_bank_card_url(bank=bank, url=card.url, card_name=card.name)

        print(f"\n💾 Saved {len(cards)} URLs to database for later scraping")
        print(f"\nTo scrape a card, run:")
        print(f"  python scripts/scrape_bank.py scrape <url>")

        return cards

    finally:
        await scraper.close()


async def scrape_card_page(url: str, bank: str = None):
    """Scrape a credit card page and generate analysis prompt"""
    print(f"\n🔍 Scraping credit card page...")
    print(f"   URL: {url}")
    print("=" * 60)

    scraper = BankScraper()

    try:
        page = await scraper.scrape_card_page(url)

        print(f"\n✅ Page scraped successfully!")
        print(f"   Title: {page.title}")
        print(f"   Content length: {len(page.text_content)} chars")

        # Guess bank from URL if not provided
        if not bank:
            url_lower = url.lower()
            if "bmo.com" in url_lower:
                bank = "BMO"
            elif "td.com" in url_lower:
                bank = "TD"
            elif "rbc" in url_lower:
                bank = "RBC"
            elif "cibc.com" in url_lower:
                bank = "CIBC"
            elif "scotiabank.com" in url_lower:
                bank = "Scotiabank"
            elif "americanexpress.com" in url_lower:
                bank = "AMEX"
            elif "tangerine.ca" in url_lower:
                bank = "Tangerine"
            elif "simplii.com" in url_lower:
                bank = "Simplii"
            elif "rogers" in url_lower:
                bank = "Rogers"
            elif "desjardins.com" in url_lower:
                bank = "Desjardins"
            elif "hsbc.ca" in url_lower:
                bank = "HSBC"
            elif "nbc.ca" in url_lower:
                bank = "National Bank"
            else:
                bank = "Unknown"

        # Generate analysis prompt
        prompt = create_analysis_prompt(
            page_content=page.text_content,
            bank=bank,
            url=url,
        )

        # Save scraped content
        output_dir = Path(__file__).parent.parent / "data" / "scraped"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() or c in "-_ " else "_" for c in page.title[:50])
        output_file = output_dir / f"{bank}_{safe_title}_{timestamp}.txt"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"URL: {url}\n")
            f.write(f"Bank: {bank}\n")
            f.write(f"Title: {page.title}\n")
            f.write(f"Scraped at: {datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n\n")
            f.write("## Page Content:\n\n")
            f.write(page.text_content)
            f.write("\n\n" + "=" * 60 + "\n\n")
            f.write("## Analysis Prompt for Claude:\n\n")
            f.write(prompt)

        print(f"\n💾 Saved to: {output_file}")

        # Print a preview
        print(f"\n📋 Content Preview (first 1000 chars):")
        print("-" * 40)
        print(page.text_content[:1000])
        print("-" * 40)

        print(f"\n🤖 To analyze this card, copy the Analysis Prompt from:")
        print(f"   {output_file}")
        print(f"\n   Or use the prompt below and give it to Claude to analyze.")

        return page, prompt

    finally:
        await scraper.close()


def list_banks():
    """List all supported banks"""
    print("\n📋 Supported Banks:")
    print("=" * 60)

    scraper = BankScraper()
    for bank, url in scraper.BANK_CARD_LISTINGS.items():
        print(f"  • {bank}")
        print(f"    {url}\n")


def show_unscraped():
    """Show URLs that haven't been scraped yet"""
    db = Database()
    urls = db.get_unscraped_urls()

    print(f"\n📋 Unscraped URLs ({len(urls)} total):")
    print("=" * 60)

    for url_info in urls:
        print(f"  • [{url_info['bank']}] {url_info.get('card_name', 'Unknown')}")
        print(f"    {url_info['url']}\n")


def main():
    print_banner()

    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Error: Playwright not installed!")
        print("   Run: pip install playwright && playwright install")
        sys.exit(1)

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "discover":
        if len(sys.argv) < 3:
            print("Error: Please provide bank name")
            print("Usage: python scripts/scrape_bank.py discover <bank>")
            sys.exit(1)
        bank = sys.argv[2]
        asyncio.run(discover_cards(bank))

    elif command == "scrape":
        if len(sys.argv) < 3:
            print("Error: Please provide URL")
            print("Usage: python scripts/scrape_bank.py scrape <url>")
            sys.exit(1)
        url = sys.argv[2]
        bank = sys.argv[3] if len(sys.argv) > 3 else None
        asyncio.run(scrape_card_page(url, bank))

    elif command == "list-banks":
        list_banks()

    elif command == "unscraped":
        show_unscraped()

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
