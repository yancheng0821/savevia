"""
Configuration management for usage guide scraper
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
SCRAPER_BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = SCRAPER_BASE_DIR / "output"
CACHE_DIR = SCRAPER_BASE_DIR / "cache"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Supported languages
LANGUAGES = ["en", "zh", "fr", "es", "ja", "ko"]
LANGUAGE_NAMES = {
    "en": "English",
    "zh": "Simplified Chinese",
    "fr": "French",
    "es": "Spanish",
    "ja": "Japanese",
    "ko": "Korean"
}

# Request configuration
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-CA,en-US;q=0.9,en;q=0.8',
}
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 2  # seconds between requests

# Review site URLs
REVIEW_SITES = {
    "creditcardgenius": {
        "base_url": "https://creditcardgenius.ca",
        "card_detail_pattern": "/credit-cards/{card-slug}",
        "review_pattern": "/best-credit-cards/{card-slug}-review",
        "list_pages": [
            "/best-credit-cards/cash-back",
            "/best-credit-cards/rewards",
            "/best-credit-cards/travel",
            "/best-credit-cards/no-fee",
        ]
    },
    "ratehub": {
        "base_url": "https://www.ratehub.ca",
        "card_detail_pattern": "/credit-cards/card/{card-slug}",
        "review_pattern": "/blog/review-{card-slug}/",
        "list_pages": [
            "/credit-cards/cash-back",
            "/credit-cards/rewards",
            "/credit-cards/travel",
            "/credit-cards/no-fee",
        ]
    },
    "princeoftravel": {
        "base_url": "https://princeoftravel.com",
        "card_detail_pattern": "/credit-cards/{card-slug}",
        "review_pattern": "/credit-cards/{card-slug}",
        "list_pages": [
            "/credit-cards",
        ]
    },
    "nerdwallet": {
        "base_url": "https://www.nerdwallet.com/ca",
        "card_detail_pattern": "/p/reviews/credit-cards/{card-slug}",
        "review_pattern": "/p/reviews/credit-cards/{card-slug}",
        "list_pages": [
            "/best/credit-cards/cash-back",
            "/best/credit-cards/travel-rewards",
        ]
    }
}

# Card slug mappings for Credit Card Genius (card_id -> slug)
# URL pattern: https://creditcardgenius.ca/credit-cards/{slug}
CCG_CARD_SLUGS = {
    # AMEX
    1: "american-express-cobalt",
    2: "american-express-gold-rewards",
    3: "american-express-platinum",
    4: "american-express-simplycash-preferred",
    5: "american-express-simplycash",
    6: "american-express-aeroplan",
    7: "american-express-aeroplan-reserve",
    # TD
    8: "td-cash-back-visa-infinite",
    9: "td-first-class-travel-visa-infinite",
    10: "td-aeroplan-visa-infinite",
    11: "td-aeroplan-visa-infinite-privilege",
    12: "td-cash-back-visa",
    # RBC
    13: "rbc-avion-visa-infinite",
    14: "rbc-avion-visa-infinite-privilege",
    15: "rbc-westjet-world-elite-mastercard",
    16: "rbc-cash-back-mastercard",
    17: "rbc-ion-visa",
    # Scotiabank
    18: "scotiabank-gold-american-express",
    19: "scotiabank-passport-visa-infinite",
    20: "scotiabank-momentum-visa-infinite",
    21: "scotiabank-scene-visa",
    # CIBC
    22: "cibc-aventura-visa-infinite",
    23: "cibc-aventura-visa-infinite-privilege",
    24: "cibc-aeroplan-visa-infinite",
    25: "cibc-dividend-visa-infinite",
    26: "cibc-costco-mastercard",
    # BMO
    27: "bmo-eclipse-visa-infinite",
    28: "bmo-cashback-world-elite-mastercard",
    29: "bmo-air-miles-world-elite-mastercard",
    30: "bmo-cashback-mastercard",
    # Rogers
    31: "rogers-world-elite-mastercard",
    32: "rogers-platinum-mastercard",
    # Tangerine
    33: "tangerine-money-back-credit-card",
    34: "tangerine-world-mastercard",
    # Neo
    35: "neo-world-elite-mastercard",
    36: "neo-world-mastercard",
    # PC Financial
    37: "pc-world-elite-mastercard",
    38: "pc-world-mastercard",
    # Simplii
    39: "simplii-cash-back-visa",
    # MBNA
    40: "mbna-rewards-world-elite-mastercard",
    41: "mbna-true-line-gold-mastercard",
    # National Bank
    42: "national-bank-world-elite-mastercard",
    # Home Trust
    43: "home-trust-preferred-visa",
    # Desjardins
    47: "desjardins-cash-back-world-elite-mastercard",
    48: "desjardins-cash-back-mastercard",
    # Canadian Tire
    49: "triangle-world-elite-mastercard",
    50: "triangle-mastercard",
    # Vancity
    51: "vancity-enviro-visa-infinite",
    52: "vancity-enviro-visa-classic",
    # Wealthsimple
    46: "wealthsimple-visa-infinite",
    # BMO Ascend
    55: "bmo-ascend-world-elite-mastercard",
    # Walmart
    56: "walmart-rewards-mastercard",
    # MBNA Amazon
    57: "mbna-amazon-rewards-mastercard",
}

# Card slug mappings for Ratehub (card_id -> slug)
# URL pattern: https://www.ratehub.ca/credit-cards/card/{slug}
RATEHUB_CARD_SLUGS = {
    # AMEX
    1: "american-express-cobalt-card",
    2: "american-express-gold-rewards-card",
    3: "american-express-platinum-card",
    4: "american-express-simplycash-preferred-card",
    5: "american-express-simplycash-card",
    6: "american-express-aeroplan-card",
    7: "american-express-aeroplan-reserve-card",
    # TD
    8: "td-cash-back-visa-infinite",
    9: "td-first-class-travel-visa-infinite",
    10: "td-aeroplan-visa-infinite",
    11: "td-aeroplan-visa-infinite-privilege-card",
    12: "td-cash-back-visa-card",
    # RBC
    13: "rbc-avion-visa-infinite",
    14: "rbc-avion-visa-infinite-privilege",
    15: "rbc-westjet-world-elite-mastercard",
    16: "rbc-cash-back-mastercard",
    17: "rbc-ion-visa",
    # Scotiabank
    18: "scotiabank-gold-american-express-card",
    19: "scotiabank-passport-visa-infinite-card",
    20: "scotiabank-momentum-visa-infinite-card",
    21: "scotiabank-scene-visa-card",
    # CIBC
    22: "cibc-aventura-visa-infinite-card",
    23: "cibc-aventura-visa-infinite-privilege-card",
    24: "cibc-aeroplan-visa-infinite-card",
    25: "cibc-dividend-visa-infinite-card",
    26: "cibc-costco-mastercard",
    # BMO
    27: "bmo-eclipse-visa-infinite-card",
    28: "bmo-cashback-world-elite-mastercard",
    29: "bmo-air-miles-world-elite-mastercard",
    30: "bmo-cashback-mastercard",
    # Rogers
    31: "rogers-world-elite-mastercard",
    32: "rogers-platinum-mastercard",
    # Tangerine
    33: "tangerine-money-back-credit-card",
    34: "tangerine-world-mastercard",
    # Neo
    35: "neo-world-elite-mastercard",
    36: "neo-world-mastercard",
    # PC Financial
    37: "pc-world-elite-mastercard",
    38: "pc-world-mastercard",
    # Simplii
    39: "simplii-cash-back-visa-card",
    # MBNA
    40: "mbna-rewards-world-elite-mastercard",
    41: "mbna-true-line-gold-mastercard",
    # National Bank
    42: "national-bank-world-elite-mastercard",
    # Home Trust
    43: "home-trust-preferred-visa-card",
}

# Bank configuration for direct scraping
BANK_CONFIGS = {
    "AMEX": {
        "domain": "americanexpress.com",
        "card_page_selectors": {
            "benefits": ".benefits-list, .card-benefits, [data-benefits]",
            "rewards": ".rewards-section, .earn-points",
            "terms": ".terms-conditions, .legal-text"
        }
    },
    "TD": {
        "domain": "td.com",
        "card_page_selectors": {
            "benefits": ".card-benefits, .feature-list",
            "rewards": ".rewards-info, .earn-section",
            "terms": ".terms, .disclosures"
        }
    },
    "RBC": {
        "domain": "rbcroyalbank.com",
        "card_page_selectors": {
            "benefits": ".card-features, .benefits",
            "rewards": ".rewards-details",
            "terms": ".legal-disclosure"
        }
    },
    "Scotiabank": {
        "domain": "scotiabank.com",
        "card_page_selectors": {
            "benefits": ".card-benefits, .features-list",
            "rewards": ".scene-rewards, .rewards-info",
            "terms": ".terms-section"
        }
    },
    "CIBC": {
        "domain": "cibc.com",
        "card_page_selectors": {
            "benefits": ".benefits-section, .card-perks",
            "rewards": ".rewards-overview",
            "terms": ".legal-terms"
        }
    },
    "BMO": {
        "domain": "bmo.com",
        "card_page_selectors": {
            "benefits": ".card-benefits, .features",
            "rewards": ".rewards-section",
            "terms": ".terms"
        }
    }
}

# Card slug mappings for Prince of Travel (card_id -> slug)
# URL pattern: https://princeoftravel.com/credit-cards/{slug}
POT_CARD_SLUGS = {
    # AMEX
    1: "american-express-cobalt-card",
    2: "american-express-gold-rewards-card",
    3: "american-express-platinum-card",
    4: "american-express-simplycash-preferred-card",
    5: "american-express-simplycash-card",
    6: "american-express-aeroplan-card",
    7: "american-express-aeroplan-reserve-card",
    # TD
    8: "td-cash-back-visa-infinite-card",
    9: "td-first-class-travel-visa-infinite-card",
    10: "td-aeroplan-visa-infinite-card",
    11: "td-aeroplan-visa-infinite-privilege-card",
    # RBC
    13: "rbc-avion-visa-infinite-card",
    14: "rbc-avion-visa-infinite-privilege-card",
    15: "rbc-westjet-world-elite-mastercard",
    # Scotiabank
    18: "scotiabank-gold-american-express-card",
    19: "scotiabank-passport-visa-infinite-card",
    # CIBC
    22: "cibc-aventura-visa-infinite-card",
    24: "cibc-aeroplan-visa-infinite-card",
    # BMO
    27: "bmo-eclipse-visa-infinite-card",
    55: "bmo-ascend-world-elite-mastercard",
}

# Card slug mappings for NerdWallet (card_id -> slug)
# URL pattern: https://www.nerdwallet.com/ca/p/reviews/credit-cards/{slug}
NERDWALLET_CARD_SLUGS = {
    # AMEX
    1: "american-express-cobalt-card-review",
    2: "american-express-gold-rewards-card-review",
    3: "american-express-platinum-card-review",
    6: "american-express-aeroplan-card-review",
    7: "american-express-aeroplan-reserve-card-review",
    # TD
    8: "td-cash-back-visa-infinite-review",
    10: "td-aeroplan-visa-infinite-review",
    # Scotiabank
    19: "scotiabank-passport-visa-infinite-card-review",
    20: "scotiabank-momentum-visa-infinite-card-review",
    # CIBC
    25: "cibc-dividend-visa-infinite-card-review",
    # BMO
    28: "bmo-cashback-world-elite-mastercard-review",
    # Tangerine
    33: "tangerine-money-back-credit-card-review",
    34: "tangerine-world-mastercard-review",
}

# Card ID to slug mapping (to be populated from database or config file)
# This maps our internal card IDs to the URL slugs used by review sites
CARD_SLUG_MAPPING = {
    # Example: 1: {"bank": "amex", "slug": "cobalt-card"}
}

# Translation prompt template
TRANSLATION_PROMPT = """You are a professional translator specializing in credit card and financial content.

Translate the following credit card usage tip from English to {target_languages}.

The content should be:
- Natural and fluent in each target language
- Accurate for financial/credit card terminology
- Concise and clear

English text:
Title: {title}
Content: {content}

Respond in JSON format:
{{
  "title": {{"zh": "...", "fr": "...", "es": "...", "ja": "...", "ko": "..."}},
  "content": {{"zh": "...", "fr": "...", "es": "...", "ja": "...", "ko": "..."}}
}}

Only output the JSON, no additional text."""

# AI Extraction prompt for analyzing credit card pages
AI_EXTRACTION_PROMPT = """You are an expert credit card analyst. Analyze the following credit card review content and extract structured usage tips.

Credit Card: {card_name} from {bank}

Content to analyze:
{content}

Extract the following information as JSON:
{{{{
  "tips": [
    {{{{
      "type": "BEST_USE|REDEMPTION|TRAVEL_BENEFIT|INSURANCE|PERK|AVOID|STACKING",
      "title": "Short title (max 50 chars)",
      "content": "Detailed explanation (max 200 chars)",
      "icon": "dining|grocery|gas|travel|transfer|hotel|insurance|shopping|streaming|warning|gift|default",
      "priority": 0-10 (lower = more important)
    }}}}
  ]
}}}}

Guidelines:
- BEST_USE: Best spending categories, earning rates, optimal usage scenarios
- REDEMPTION: How to redeem points, transfer partners, point values, best redemption strategies
- TRAVEL_BENEFIT: Airport lounge access, travel credits, companion tickets, hotel status
- INSURANCE: Travel insurance, purchase protection, rental car insurance
- PERK: Other benefits like credits, memberships, statement credits
- AVOID: Things to avoid, limitations, better alternatives for certain categories
- STACKING: How to combine with other cards or offers

Focus on actionable, practical tips that help cardholders maximize value.
Only include tips that are specific and valuable. Skip generic information.
Return valid JSON only, no additional text."""

# Known transfer partners for different points programs
TRANSFER_PARTNERS = {
    "Aeroplan": [
        {"partner": "Air Canada", "ratio": "1:1", "type": "AIRLINE"},
        {"partner": "Star Alliance", "ratio": "1:1", "type": "AIRLINE"},
        {"partner": "Marriott Bonvoy", "ratio": "1:1", "type": "HOTEL"},
    ],
    "Scene+": [
        {"partner": "Empire (Sobeys/FreshCo)", "ratio": "varies", "type": "RETAIL"},
        {"partner": "Cineplex", "ratio": "varies", "type": "ENTERTAINMENT"},
    ],
    "Membership Rewards": [
        {"partner": "Aeroplan", "ratio": "1:1", "type": "AIRLINE"},
        {"partner": "British Airways Avios", "ratio": "1:1", "type": "AIRLINE"},
        {"partner": "Hilton Honors", "ratio": "1:2", "type": "HOTEL"},
        {"partner": "Marriott Bonvoy", "ratio": "1:1", "type": "HOTEL"},
    ],
    "TD Rewards": [
        {"partner": "Expedia for TD", "ratio": "varies", "type": "TRAVEL"},
    ],
    "RBC Avion": [
        {"partner": "British Airways", "ratio": "varies", "type": "AIRLINE"},
        {"partner": "Cathay Pacific", "ratio": "varies", "type": "AIRLINE"},
    ]
}
