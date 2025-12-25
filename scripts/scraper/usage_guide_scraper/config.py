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
    }
}

# Card slug mappings for known cards (card_id -> slug)
CARD_SLUGS = {
    1: "american-express-cobalt-card",
    2: "american-express-gold-rewards-card",
    3: "td-aeroplan-visa-infinite-card",
    4: "td-cash-back-visa-infinite-card",
    5: "scotiabank-scene-visa-card",
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
