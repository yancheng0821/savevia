#!/usr/bin/env python3
"""
Usage Guide Scraper - Main Entry Point

Scrapes credit card usage tips from bank websites and review sites,
translates content using OpenAI, and generates SQL for database updates.

Usage:
    # AI-powered extraction (recommended) - uses OpenAI to extract structured tips
    python -m usage_guide_scraper.main --source ai --card-ids 6 -o aeroplan_tips.sql

    # Traditional scraping from review sites
    python -m usage_guide_scraper.main --source review --output usage_tips_update.sql

    # Preview mode (no SQL generation)
    python -m usage_guide_scraper.main --dry-run --source ai --card-ids 6

    # Skip translation (English only)
    python -m usage_guide_scraper.main --source ai --card-ids 1,2,3 --no-translate
"""

import argparse
import sys
import json
from pathlib import Path
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from usage_guide_scraper.scrapers import (
    CreditCardGeniusUsageScraper,
    RatehubUsageScraper,
    BankScraper,
    AICardScraper,
    SingleSourceAIScraper
)
from usage_guide_scraper.translator import Translator, MockTranslator
from usage_guide_scraper.sql_generator import SQLGenerator, DryRunGenerator
from usage_guide_scraper.models import ScrapedCardData, UsageTip
from usage_guide_scraper.config import OUTPUT_DIR, OPENAI_API_KEY


def load_cards_from_database() -> List[dict]:
    """Load cards from MySQL database via Docker"""
    import subprocess
    import json as json_module

    try:
        # Query database via docker exec
        query = "SELECT id, name, bank, apply_url FROM credit_cards ORDER BY bank, id"
        cmd = [
            'docker', 'exec', 'savevia-mysql',
            'mysql', '-u', 'savevia', '-psavevia123', 'savevia',
            '-N', '-e', query
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            print(f"Database query failed: {result.stderr}")
            return _get_fallback_cards()

        cards = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    cards.append({
                        "id": int(parts[0]),
                        "name": parts[1],
                        "bank": parts[2],
                        "apply_url": parts[3] if len(parts) > 3 else None
                    })
        return cards if cards else _get_fallback_cards()

    except Exception as e:
        print(f"Failed to load from database: {e}")
        return _get_fallback_cards()


def _get_fallback_cards() -> List[dict]:
    """Fallback card data when database is not available"""
    return [
        {"id": 1, "name": "Cobalt Card", "bank": "AMEX", "apply_url": "https://www.americanexpress.com/ca/en/credit-cards/cobalt-card/"},
        {"id": 8, "name": "Cash Back Visa Infinite", "bank": "TD", "apply_url": "https://www.td.com/ca/en/personal-banking/products/credit-cards/cash-back/cash-back-visa-infinite-card"},
        {"id": 10, "name": "Aeroplan Visa Infinite", "bank": "TD", "apply_url": "https://www.td.com/ca/en/personal-banking/products/credit-cards/aeroplan/aeroplan-visa-infinite-card"},
        {"id": 20, "name": "Momentum Visa Infinite", "bank": "Scotiabank", "apply_url": "https://www.scotiabank.com/ca/en/personal/credit-cards/visa/momentum-visa-infinite-card.html"},
    ]


def load_cards_from_file(filepath: str) -> List[dict]:
    """Load cards from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def filter_cards(cards: List[dict], card_ids: Optional[List[int]] = None) -> List[dict]:
    """Filter cards by ID if specified"""
    if card_ids:
        return [c for c in cards if c.get('id') in card_ids]
    return cards


def scrape_review_sites(cards: List[dict], use_selenium: bool = True) -> List[ScrapedCardData]:
    """Scrape usage tips from review sites"""
    all_data = []

    print("\n" + "=" * 60)
    print("Scraping Credit Card Genius...")
    print("=" * 60)

    try:
        scraper = CreditCardGeniusUsageScraper(use_selenium=use_selenium)
        data = scraper.scrape_all(cards)
        all_data.extend(data)
        print(f"Found data for {len(data)} cards")
    except Exception as e:
        print(f"Error scraping Credit Card Genius: {e}")

    print("\n" + "=" * 60)
    print("Scraping Ratehub...")
    print("=" * 60)

    try:
        scraper = RatehubUsageScraper(use_selenium=use_selenium)
        data = scraper.scrape_all(cards)
        # Merge with existing data
        for scraped in data:
            # Find existing data for this card
            existing = next((d for d in all_data if d.card_id == scraped.card_id), None)
            if existing:
                # Merge tips (avoid duplicates)
                existing_titles = {t.title_en for t in existing.usage_tips}
                for tip in scraped.usage_tips:
                    if tip.title_en not in existing_titles:
                        existing.usage_tips.append(tip)
            else:
                all_data.append(scraped)
        print(f"Found data for {len(data)} cards")
    except Exception as e:
        print(f"Error scraping Ratehub: {e}")

    return all_data


def scrape_bank_sites(cards: List[dict], use_selenium: bool = True) -> List[ScrapedCardData]:
    """Scrape usage tips from bank official websites"""
    print("\n" + "=" * 60)
    print("Scraping Bank Websites...")
    print("=" * 60)

    try:
        scraper = BankScraper(use_selenium=use_selenium)
        return scraper.scrape_all(cards)
    except Exception as e:
        print(f"Error scraping bank websites: {e}")
        return []


def scrape_with_ai(cards: List[dict], use_selenium: bool = True, use_cache: bool = True) -> List[ScrapedCardData]:
    """Scrape usage tips using AI extraction from multiple sources"""
    print("\n" + "=" * 60)
    print("AI-Powered Scraping (Multiple Sources)")
    print("=" * 60)

    try:
        scraper = AICardScraper(use_selenium=use_selenium, use_cache=use_cache)
        return scraper.scrape_all(cards)
    except Exception as e:
        print(f"Error in AI scraping: {e}")
        import traceback
        traceback.print_exc()
        return []


def merge_scraped_data(data_list: List[ScrapedCardData]) -> List[ScrapedCardData]:
    """Merge data from multiple sources, avoiding duplicates"""
    merged = {}

    for data in data_list:
        if data.card_id not in merged:
            merged[data.card_id] = data
        else:
            existing = merged[data.card_id]
            # Merge tips
            existing_titles = {t.title_en for t in existing.usage_tips}
            for tip in data.usage_tips:
                if tip.title_en not in existing_titles:
                    existing.usage_tips.append(tip)
            # Update reward info if better data
            if data.reward_info and not existing.reward_info:
                existing.reward_info = data.reward_info

    return list(merged.values())


def main():
    parser = argparse.ArgumentParser(
        description='Scrape credit card usage tips and generate SQL updates'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview without generating SQL or translating'
    )
    parser.add_argument(
        '--source',
        choices=['all', 'review', 'bank', 'ai'],
        default='all',
        help='Data source to scrape: all, review, bank, or ai (default: all)'
    )
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable AI extraction cache (re-process all pages)'
    )
    parser.add_argument(
        '--card-ids',
        type=str,
        help='Comma-separated list of card IDs to scrape'
    )
    parser.add_argument(
        '--cards-file',
        type=str,
        help='JSON file with card data'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output SQL filename'
    )
    parser.add_argument(
        '--no-translate',
        action='store_true',
        help='Skip translation (English only)'
    )
    parser.add_argument(
        '--no-selenium',
        action='store_true',
        help='Use requests only (no browser automation)'
    )
    parser.add_argument(
        '--mock-translate',
        action='store_true',
        help='Use mock translator for testing'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Usage Guide Scraper")
    print("=" * 60)

    # Load cards
    if args.cards_file:
        print(f"Loading cards from: {args.cards_file}")
        cards = load_cards_from_file(args.cards_file)
    else:
        print("Loading cards from database...")
        cards = load_cards_from_database()

    # Filter by card IDs if specified
    if args.card_ids:
        card_ids = [int(x.strip()) for x in args.card_ids.split(',')]
        cards = filter_cards(cards, card_ids)
        print(f"Filtering to {len(cards)} cards: {card_ids}")

    print(f"Total cards to process: {len(cards)}")

    if not cards:
        print("No cards to process. Exiting.")
        return

    # Scrape data
    all_data = []
    use_selenium = not args.no_selenium
    use_cache = not args.no_cache

    if args.source == 'ai':
        # AI-powered extraction (recommended)
        ai_data = scrape_with_ai(cards, use_selenium, use_cache)
        all_data.extend(ai_data)
    else:
        # Traditional scraping methods
        if args.source in ['all', 'review']:
            review_data = scrape_review_sites(cards, use_selenium)
            all_data.extend(review_data)

        if args.source in ['all', 'bank']:
            bank_data = scrape_bank_sites(cards, use_selenium)
            all_data.extend(bank_data)

    # Merge data from different sources
    merged_data = merge_scraped_data(all_data)

    print("\n" + "=" * 60)
    print("Scraping Summary")
    print("=" * 60)

    total_tips = sum(len(d.usage_tips) for d in merged_data)
    print(f"Cards with data: {len(merged_data)}")
    print(f"Total tips collected: {total_tips}")

    if not merged_data:
        print("No data scraped. Exiting.")
        return

    # Collect all tips
    all_tips = []
    for data in merged_data:
        all_tips.extend(data.usage_tips)

    # Dry run - preview only
    if args.dry_run:
        print("\n[DRY RUN MODE]")
        print("Would generate the following tips:")
        print("-" * 40)
        for data in merged_data:
            print(f"\nCard {data.card_id}: {data.bank} {data.card_name}")
            for tip in data.usage_tips:
                print(f"  [{tip.tip_type.value}] {tip.title_en[:50]}...")
        return

    # Translate tips
    translated_tips = []

    if args.no_translate:
        print("\n[SKIPPING TRANSLATION]")
        # Create translated tips with English only
        from usage_guide_scraper.models import TranslatedTip
        for tip in all_tips:
            translated_tips.append(TranslatedTip(
                card_id=tip.card_id,
                tip_type=tip.tip_type,
                title_json={"en": tip.title_en},
                content_json={"en": tip.content_en},
                icon=tip.icon,
                priority=tip.priority
            ))
    else:
        print("\n" + "=" * 60)
        print("Translating Tips")
        print("=" * 60)

        if args.mock_translate:
            print("[Using mock translator]")
            translator = MockTranslator()
        else:
            if not OPENAI_API_KEY:
                print("ERROR: OPENAI_API_KEY not set. Use --no-translate or set the environment variable.")
                return
            translator = Translator()

        translated_tips = translator.batch_translate(all_tips)
        print(f"Translated {len(translated_tips)} tips")

    # Generate SQL
    print("\n" + "=" * 60)
    print("Generating SQL")
    print("=" * 60)

    reward_infos = [d.reward_info for d in merged_data if d.reward_info]

    generator = SQLGenerator()
    sql = generator.generate_sql(translated_tips, reward_infos, args.output)

    print("\nDone!")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
