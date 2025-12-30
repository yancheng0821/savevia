#!/usr/bin/env python3
"""
Fix card image URLs for already collected cards.

Scans the database for cards with invalid image URLs and extracts
the correct image URL from the source page.
"""

import asyncio
import re
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import nest_asyncio
nest_asyncio.apply()

from src.services.database import Database
from src.agents.custom_crawl_tool import OptimizedCrawler


def is_valid_image_url(url: str) -> bool:
    """Check if URL is a valid image URL."""
    if not url:
        return False
    image_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif')
    return any(url.lower().endswith(ext) or ext + '?' in url.lower() for ext in image_extensions)


async def extract_card_image(page_url: str, bank: str) -> str:
    """Extract the credit card image URL from the page HTML."""
    try:
        crawler = OptimizedCrawler(delay=2.0, max_length=None)
        result = await crawler.crawl(page_url)

        if not result['success']:
            return None

        html = result['html']

        # Find all image URLs
        all_imgs = re.findall(r'src="([^"]+\.(?:png|jpg|jpeg|webp))"', html, re.IGNORECASE)

        if not all_imgs:
            return None

        # Bank-specific image patterns
        bank_patterns = {
            'BMO': [
                r'/dist/images/.*credit-cards/[^/]+\.(png|jpg)',
            ],
            'TD': [
                r'/content/dam/.*credit-cards.*\.(png|jpg)',
                r'/personal-banking/images/.*card.*\.(png|jpg)',
            ],
            'RBC': [
                r'/.*cards/.*\.(png|jpg)',
            ],
            'CIBC': [
                r'/.*card.*\.(png|jpg)',
            ],
            'Scotiabank': [
                r'/.*card.*\.(png|jpg)',
            ],
        }

        # Get patterns for this bank
        patterns = bank_patterns.get(bank, [])

        # Try bank-specific patterns first
        for pattern in patterns:
            for img in all_imgs:
                if re.search(pattern, img, re.IGNORECASE):
                    # Make URL absolute if needed
                    if img.startswith('/'):
                        from urllib.parse import urlparse
                        parsed = urlparse(page_url)
                        img = f"{parsed.scheme}://{parsed.netloc}{img}"
                    return img

        # Fallback: look for first image with card-related keywords
        card_keywords = ['card', 'credit', 'mastercard', 'visa', 'amex']
        for img in all_imgs:
            if any(kw in img.lower() for kw in card_keywords):
                # Skip product page images, icons, logos
                skip_keywords = ['icon', 'logo', 'banner', 'hero', 'background', 'apply-now',
                               'product-page', 'mobile', 'tv', 'phone', 'mockup', 'instacart']
                if any(skip in img.lower() for skip in skip_keywords):
                    continue
                # Make URL absolute if needed
                if img.startswith('/'):
                    from urllib.parse import urlparse
                    parsed = urlparse(page_url)
                    img = f"{parsed.scheme}://{parsed.netloc}{img}"
                return img

        return None

    except Exception as e:
        print(f"  Error: {e}")
        return None


async def fix_card_images(bank: str = None, dry_run: bool = False):
    """Fix image URLs for cards in the database."""
    db = Database()

    # Get all cards
    cards = db.get_all_cards()

    # Filter by bank if specified
    if bank:
        cards = [c for c in cards if c.bank == bank]

    print(f"\nChecking {len(cards)} cards...")

    fixed_count = 0
    for card in cards:
        # Check if image URL is valid
        if is_valid_image_url(card.image_url):
            continue

        # Get source URL for the card
        source_url = card.apply_url
        if not source_url:
            print(f"  ⚠️ {card.bank} - {card.name}: No source URL")
            continue

        print(f"\n🔍 {card.bank} - {card.name}")
        print(f"   Current image: {card.image_url or 'None'}")

        # Extract correct image URL
        new_image_url = await extract_card_image(source_url, card.bank)

        if new_image_url:
            print(f"   ✅ New image: {new_image_url}")

            if not dry_run:
                # Update the database using the correct connection pattern
                conn = db._get_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "UPDATE cards SET image_url = ? WHERE id = ?",
                        (new_image_url, card.id)
                    )
                    conn.commit()
                    print(f"   ✅ Updated!")
                finally:
                    conn.close()
            else:
                print(f"   (dry run - not updated)")

            fixed_count += 1
        else:
            print(f"   ❌ Could not extract image")

    print(f"\n{'Would fix' if dry_run else 'Fixed'} {fixed_count} cards")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fix card image URLs")
    parser.add_argument("--bank", "-b", help="Only fix cards from this bank")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Don't actually update")
    args = parser.parse_args()

    asyncio.run(fix_card_images(bank=args.bank, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
