#!/usr/bin/env python3
"""
Scrape card images for savevia database cards.
Fetches images from bank websites based on card names.
"""

import asyncio
import re
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, quote
from typing import List, Dict, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import nest_asyncio
nest_asyncio.apply()

from playwright.async_api import async_playwright

# Bank-specific card page URLs and search patterns
BANK_CARD_PAGES = {
    "AMEX": {
        "base_url": "https://www.americanexpress.com/ca/en/credit-cards/",
        "cards": {
            "Cobalt Card": "https://www.americanexpress.com/ca/en/credit-cards/cobalt-card/",
            "Gold Rewards Card": "https://www.americanexpress.com/ca/en/credit-cards/gold-rewards-card/",
            "Platinum Card": "https://www.americanexpress.com/ca/en/credit-cards/platinum-card/",
            "SimplyCash Preferred": "https://www.americanexpress.com/ca/en/credit-cards/simplycash-preferred-card/",
            "SimplyCash": "https://www.americanexpress.com/ca/en/credit-cards/simplycash-card/",
            "Aeroplan Card": "https://www.americanexpress.com/ca/en/credit-cards/aeroplan-card/",
            "Aeroplan Reserve Card": "https://www.americanexpress.com/ca/en/credit-cards/aeroplan-reserve-card/",
        }
    },
    "TD": {
        "base_url": "https://www.td.com/ca/en/personal-banking/products/credit-cards/",
        "cards": {
            "Cash Back Visa Infinite": "https://www.td.com/ca/en/personal-banking/products/credit-cards/cash-back/cash-back-visa-infinite-card",
            "First Class Visa Infinite": "https://www.td.com/ca/en/personal-banking/products/credit-cards/travel-rewards/first-class-travel-visa-infinite-card",
            "Aeroplan Visa Infinite": "https://www.td.com/ca/en/personal-banking/products/credit-cards/aeroplan/aeroplan-visa-infinite-card",
            "Aeroplan Visa Infinite Privilege": "https://www.td.com/ca/en/personal-banking/products/credit-cards/aeroplan/aeroplan-visa-infinite-privilege-card",
            "Cash Back Visa": "https://www.td.com/ca/en/personal-banking/products/credit-cards/cash-back/cash-back-visa-card",
        }
    },
    "RBC": {
        "base_url": "https://www.rbcroyalbank.com/credit-cards/",
        "cards": {
            "Avion Visa Infinite": "https://www.rbcroyalbank.com/credit-cards/travel/rbc-avion-visa-infinite.html",
            "Avion Visa Infinite Privilege": "https://www.rbcroyalbank.com/credit-cards/travel/rbc-avion-visa-infinite-privilege.html",
            "WestJet World Elite Mastercard": "https://www.rbcroyalbank.com/credit-cards/travel/rbc-westjet-world-elite-mastercard.html",
            "Cash Back Mastercard": "https://www.rbcroyalbank.com/credit-cards/cash-back/rbc-cash-back-mastercard.html",
            "ION Visa": "https://www.rbcroyalbank.com/credit-cards/cash-back/rbc-ion-visa.html",
            "ION+ Visa": "https://www.rbcroyalbank.com/credit-cards/cash-back/rbc-ion-plus-visa.html",
        }
    },
    "CIBC": {
        "base_url": "https://www.cibc.com/en/personal-banking/credit-cards/",
        "cards": {
            "Aventura Visa Infinite": "https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/aventura-visa-infinite-card.html",
            "Aventura Visa Infinite Privilege": "https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/aventura-visa-infinite-privilege-card.html",
            "Aeroplan Visa Infinite": "https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/aeroplan-visa-infinite-card.html",
            "Aeroplan Visa Card": "https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/aeroplan-visa-card.html",
            "Dividend Visa Infinite": "https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/dividend-visa-infinite-card.html",
            "Dividend Visa Card": "https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/dividend-visa-card.html",
            "Costco Mastercard": "https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/costco-mastercard.html",
            "Adapta Mastercard": "https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/adapta-mastercard.html",
        }
    },
    "Scotiabank": {
        "base_url": "https://www.scotiabank.com/ca/en/personal/credit-cards/",
        "cards": {
            "Gold American Express": "https://www.scotiabank.com/ca/en/personal/credit-cards/visa/scotiabank-gold-american-express-card.html",
            "Passport Visa Infinite": "https://www.scotiabank.com/ca/en/personal/credit-cards/visa/passport-visa-infinite-card.html",
            "Momentum Visa Infinite": "https://www.scotiabank.com/ca/en/personal/credit-cards/visa/momentum-visa-infinite-card.html",
            "Scene+ Visa": "https://www.scotiabank.com/ca/en/personal/credit-cards/visa/scene-visa-card.html",
        }
    },
    "BMO": {
        "base_url": "https://www.bmo.com/main/personal/credit-cards/",
        "cards": {
            "Eclipse Visa Infinite": "https://www.bmo.com/main/personal/credit-cards/bmo-eclipse-visa-infinite/",
            "CashBack World Elite Mastercard": "https://www.bmo.com/main/personal/credit-cards/bmo-cashback-world-elite-mastercard/",
            "CashBack Mastercard": "https://www.bmo.com/main/personal/credit-cards/bmo-cashback-mastercard/",
            "Air Miles World Elite Mastercard": "https://www.bmo.com/main/personal/credit-cards/bmo-air-miles-world-elite-mastercard/",
            "Ascend World Elite Mastercard": "https://www.bmo.com/main/personal/credit-cards/bmo-ascend-world-elite-mastercard/",
        }
    },
    "Rogers": {
        "base_url": "https://www.rogersbank.com/en/",
        "cards": {
            "Red World Elite Mastercard": "https://www.rogersbank.com/en/rogers_world_elite_mastercard",
            "Red Mastercard": "https://www.rogersbank.com/en/rogers_platinum_mastercard",
        }
    },
    "Tangerine": {
        "base_url": "https://www.tangerine.ca/en/products/spending/creditcard",
        "cards": {
            "Money-Back Credit Card": "https://www.tangerine.ca/en/products/spending/creditcard/money-back",
            "World Mastercard": "https://www.tangerine.ca/en/products/spending/creditcard/world",
        }
    },
    "Neo": {
        "base_url": "https://www.neofinancial.com/",
        "cards": {
            "World Elite Mastercard": "https://www.neofinancial.com/credit",
            "World Mastercard": "https://www.neofinancial.com/credit",
        }
    },
    "PC Financial": {
        "base_url": "https://www.pcfinancial.ca/en/credit-cards/",
        "cards": {
            "World Elite Mastercard": "https://www.pcfinancial.ca/en/credit-cards/pc-money-account",
            "World Mastercard": "https://www.pcfinancial.ca/en/credit-cards/pc-money-account",
        }
    },
    "Simplii": {
        "base_url": "https://www.simplii.com/en/credit-cards.html",
        "cards": {
            "Cash Back Visa Card": "https://www.simplii.com/en/credit-cards/cash-back-visa-card.html",
        }
    },
    "MBNA": {
        "base_url": "https://www.mbna.ca/en/credit-cards/",
        "cards": {
            "Rewards World Elite Mastercard": "https://www.mbna.ca/en/credit-cards/rewards/mbna-rewards-world-elite-mastercard.html",
            "True Line Gold Mastercard": "https://www.mbna.ca/en/credit-cards/low-rate/mbna-true-line-gold-mastercard.html",
            "Amazon.ca Rewards Mastercard": "https://www.amazon.ca/dp/B08N3F1W7S",
        }
    },
    "Canadian Tire": {
        "base_url": "https://triangle.canadiantire.ca/en/credit-cards.html",
        "cards": {
            "Triangle World Elite Mastercard": "https://triangle.canadiantire.ca/en/credit-cards/triangle-world-elite-mastercard.html",
            "Triangle Mastercard": "https://triangle.canadiantire.ca/en/credit-cards/triangle-mastercard.html",
        }
    },
    "Desjardins": {
        "base_url": "https://www.desjardins.com/ca/personal/loans-credit/credit-cards/",
        "cards": {
            "Cash Back World Elite Mastercard": "https://www.desjardins.com/ca/personal/loans-credit/credit-cards/cash-back-world-elite-mastercard/index.jsp",
            "Cash Back Mastercard": "https://www.desjardins.com/ca/personal/loans-credit/credit-cards/cash-back-mastercard/index.jsp",
        }
    },
    "Wealthsimple": {
        "base_url": "https://www.wealthsimple.com/en-ca/cash-card",
        "cards": {
            "Visa Infinite": "https://www.wealthsimple.com/en-ca/cash-card",
        }
    },
    "National Bank": {
        "base_url": "https://www.nbc.ca/personal/credit-cards.html",
        "cards": {
            "World Elite Mastercard": "https://www.nbc.ca/personal/credit-cards/mastercard-world-elite.html",
        }
    },
    "Vancity": {
        "base_url": "https://www.vancity.com/Banking/CreditCards/",
        "cards": {
            "enviro Visa Infinite": "https://www.vancity.com/Banking/CreditCards/enviro-visa-infinite/",
            "enviro Visa Classic": "https://www.vancity.com/Banking/CreditCards/enviro-visa/",
        }
    },
    "Walmart": {
        "base_url": "https://www.walmartrewards.ca/",
        "cards": {
            "Rewards Mastercard": "https://www.walmartrewards.ca/credit-card/",
        }
    },
    "Home Trust": {
        "base_url": "https://www.hometrust.ca/credit-cards/",
        "cards": {
            "Preferred Visa": "https://www.hometrust.ca/credit-cards/preferred-visa-card/",
        }
    },
    "Meridian": {
        "base_url": "https://www.meridiancu.ca/personal/credit-cards",
        "cards": {
            "Visa Infinite Cash Back": "https://www.meridiancu.ca/personal/credit-cards/visa-infinite-cash-back",
            "Visa Cash Back": "https://www.meridiancu.ca/personal/credit-cards/visa-cash-back",
        }
    },
    "Coast Capital": {
        "base_url": "https://www.coastcapitalsavings.com/credit-cards",
        "cards": {
            "Cash Back Mastercard": "https://www.coastcapitalsavings.com/credit-cards/cash-back-mastercard",
        }
    },
}


def get_savevia_cards() -> List[Dict]:
    """Get cards from savevia MySQL database."""
    try:
        result = subprocess.run(
            ['docker', 'exec', 'savevia-mysql', 'mysql', '-u', 'savevia', '-psavevia123', 'savevia', '-N', '-e',
             'SELECT id, bank, name FROM credit_cards ORDER BY bank, name;'],
            capture_output=True,
            text=True
        )

        cards = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    cards.append({
                        'id': int(parts[0]),
                        'bank': parts[1],
                        'name': parts[2]
                    })
        return cards
    except Exception as e:
        print(f"Error getting cards from database: {e}")
        return []


async def scrape_card_image(url: str, card_name: str, bank: str) -> Optional[str]:
    """Scrape image from a card's official page."""
    print(f"  Scraping: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-CA'
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)

            html = await page.content()

            # Find all image URLs
            all_imgs = re.findall(r'src="([^"]+\.(?:png|jpg|jpeg|webp)(?:\?[^"]*)?)"', html, re.IGNORECASE)

            # Also check srcset for responsive images
            srcset_imgs = re.findall(r'srcset="([^"]+)"', html, re.IGNORECASE)
            for srcset in srcset_imgs:
                urls = re.findall(r'(https?://[^\s,]+\.(?:png|jpg|jpeg|webp)[^\s,]*)', srcset)
                all_imgs.extend(urls)

            # Filter for card images
            card_keywords = ['card', 'credit', 'product', 'hero']
            skip_keywords = ['icon', 'logo', 'banner', 'mobile', 'tv', 'phone', 'badge', 'button',
                           'arrow', 'check', 'x-mark', 'avatar', 'profile', 'facebook', 'twitter',
                           'instagram', 'linkedin', 'youtube', 'pinterest', 'app-store', 'google-play']

            for img in all_imgs:
                img_lower = img.lower()

                # Skip non-card images
                if any(skip in img_lower for skip in skip_keywords):
                    continue

                # Prefer card-related images
                if any(kw in img_lower for kw in card_keywords):
                    img_url = make_absolute_url(img, url)
                    return img_url

            # Fallback: return first suitable image
            for img in all_imgs:
                img_lower = img.lower()
                if not any(skip in img_lower for skip in skip_keywords):
                    if 'png' in img_lower or 'jpg' in img_lower or 'jpeg' in img_lower:
                        img_url = make_absolute_url(img, url)
                        return img_url

            return None

        except Exception as e:
            print(f"    Error: {e}")
            return None
        finally:
            await context.close()
            await browser.close()


def make_absolute_url(img_url: str, page_url: str) -> str:
    """Convert relative URL to absolute URL."""
    if img_url.startswith('http'):
        return img_url
    if img_url.startswith('//'):
        return 'https:' + img_url
    if img_url.startswith('/'):
        parsed = urlparse(page_url)
        return f"{parsed.scheme}://{parsed.netloc}{img_url}"
    return img_url


async def scrape_all_cards():
    """Main function to scrape images for all savevia cards."""
    print("=" * 60)
    print("Scraping images for Savevia credit cards")
    print("=" * 60)

    # Get cards from database
    cards = get_savevia_cards()
    print(f"\nFound {len(cards)} cards in database\n")

    results = []
    success_count = 0

    for card in cards:
        card_id = card['id']
        bank = card['bank']
        name = card['name']

        print(f"\n[{card_id}] {bank} - {name}")

        # Find URL for this card
        bank_config = BANK_CARD_PAGES.get(bank)
        if not bank_config:
            print(f"  No URL mapping for bank: {bank}")
            results.append({
                'id': card_id,
                'bank': bank,
                'name': name,
                'url': None,
                'image_url': None,
                'error': 'Bank not configured'
            })
            continue

        card_url = bank_config['cards'].get(name)
        if not card_url:
            # Try fuzzy match
            for card_name, url in bank_config['cards'].items():
                if name.lower() in card_name.lower() or card_name.lower() in name.lower():
                    card_url = url
                    break

        if not card_url:
            print(f"  No URL found for card: {name}")
            results.append({
                'id': card_id,
                'bank': bank,
                'name': name,
                'url': None,
                'image_url': None,
                'error': 'Card URL not found'
            })
            continue

        # Scrape the image
        image_url = await scrape_card_image(card_url, name, bank)

        if image_url:
            print(f"  ✅ Found: {image_url[:80]}...")
            success_count += 1
        else:
            print(f"  ❌ No image found")

        results.append({
            'id': card_id,
            'bank': bank,
            'name': name,
            'url': card_url,
            'image_url': image_url,
        })

        # Add delay between requests
        await asyncio.sleep(1)

    # Save results
    output_dir = Path(__file__).parent.parent / "data" / "images"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"savevia_cards_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"Results: {success_count}/{len(cards)} cards have images")
    print(f"Saved to: {output_file}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    asyncio.run(scrape_all_cards())
