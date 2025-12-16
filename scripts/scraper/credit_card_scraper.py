#!/usr/bin/env python3
"""
Canadian Credit Card Data Scraper
Scrapes credit card information from Credit Card Genius and Ratehub.
Generates incremental SQL statements for database updates.

Usage:
    python credit_card_scraper.py [--dry-run] [--output FILE]

Data Sources:
    - Credit Card Genius (creditcardgenius.ca) - Primary source
    - Ratehub (ratehub.ca) - Secondary/verification source

Note: Does NOT scrape bank websites directly to avoid IP bans.
"""

import json
import re
import time
import argparse
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
import hashlib

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Warning: Selenium not installed. Run: pip install selenium")

# For fallback HTTP requests
import requests
from bs4 import BeautifulSoup

# ============================================
# Configuration
# ============================================

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-CA,en-US;q=0.9,en;q=0.8',
}

# Spending categories matching the backend enum
CATEGORIES = [
    'DINING', 'GROCERY', 'GAS', 'TRAVEL', 'STREAMING', 'TRANSIT',
    'PHARMACY', 'RENT', 'RECURRING', 'ONLINE_SHOPPING', 'FOREIGN',
    'RETAIL', 'ENTERTAINMENT', 'PERSONAL_SERVICES', 'HOME_IMPROVEMENT',
    'WHOLESALE', 'INSURANCE', 'TELECOM', 'EV_CHARGING', 'OTHER'
]

# Category keyword mapping for parsing reward descriptions
CATEGORY_KEYWORDS = {
    'DINING': ['dining', 'restaurant', 'food', 'eat', 'meal', 'cafe', 'bar'],
    'GROCERY': ['grocery', 'groceries', 'supermarket', 'food store', 'loblaw', 'sobeys', 'metro', 'safeway', 'iga', 'no frills', 'loblaws'],
    'GAS': ['gas', 'fuel', 'petrol', 'esso', 'shell', 'petro-canada', 'pioneer'],
    'TRAVEL': ['travel', 'hotel', 'flight', 'airline', 'air canada', 'westjet', 'marriott', 'hilton', 'expedia'],
    'STREAMING': ['streaming', 'netflix', 'spotify', 'disney+', 'amazon prime', 'apple tv', 'crave'],
    'TRANSIT': ['transit', 'public transport', 'uber', 'lyft', 'taxi', 'bus', 'subway', 'presto', 'rideshare'],
    'PHARMACY': ['pharmacy', 'drug store', 'shoppers', 'rexall', 'london drugs', 'pharma'],
    'RENT': ['rent', 'rental', 'landlord', 'plastiq'],
    'RECURRING': ['recurring', 'subscription', 'bill', 'utility', 'utilities', 'pre-authorized', 'automatic payment'],
    'ONLINE_SHOPPING': ['online', 'amazon', 'e-commerce', 'digital purchase'],
    'FOREIGN': ['foreign', 'international', 'fx', 'currency', 'abroad', 'u.s.', 'usd', 'no fx fee'],
    'RETAIL': ['retail', 'shopping', 'store', 'purchase'],
    'ENTERTAINMENT': ['entertainment', 'movie', 'theatre', 'concert', 'sport', 'game'],
    'PERSONAL_SERVICES': ['personal service', 'spa', 'salon', 'beauty', 'haircut', 'barber'],
    'HOME_IMPROVEMENT': ['home improvement', 'hardware', 'home depot', 'rona', 'lowes', 'renovation'],
    'WHOLESALE': ['wholesale', 'costco', 'bulk'],
    'INSURANCE': ['insurance'],
    'TELECOM': ['telecom', 'phone', 'mobile', 'internet', 'rogers', 'bell', 'telus', 'fido', 'shaw', 'freedom'],
    'EV_CHARGING': ['ev', 'electric vehicle', 'charging', 'charger'],
}

# Bank name normalization
BANK_ALIASES = {
    'american express': 'AMEX',
    'amex': 'AMEX',
    'td bank': 'TD',
    'td canada trust': 'TD',
    'royal bank': 'RBC',
    'rbc royal bank': 'RBC',
    'bank of montreal': 'BMO',
    'scotiabank': 'Scotiabank',
    'scotia': 'Scotiabank',
    'cibc': 'CIBC',
    'national bank': 'National Bank',
    'banque nationale': 'National Bank',
    'tangerine': 'Tangerine',
    'simplii': 'Simplii',
    'simplii financial': 'Simplii',
    'pc financial': 'PC Financial',
    'president\'s choice': 'PC Financial',
    'rogers bank': 'Rogers',
    'rogers': 'Rogers',
    'neo financial': 'Neo',
    'neo': 'Neo',
    'mbna': 'MBNA',
    'home trust': 'Home Trust',
    'hsbc': 'HSBC',
    'desjardins': 'Desjardins',
    'brim': 'Brim',
    'canadian tire': 'Canadian Tire',
    'triangle': 'Canadian Tire',
}

# Card type detection
CARD_TYPE_PATTERNS = {
    'AMEX': ['american express', 'amex'],
    'VISA': ['visa'],
    'MASTERCARD': ['mastercard', 'master card', 'mc'],
}


# ============================================
# Data Classes
# ============================================

@dataclass
class RewardRule:
    category: str
    reward_rate: float  # As decimal, e.g., 0.05 for 5%
    monthly_cap: Optional[float] = None
    description: str = ""

    def to_dict(self) -> dict:
        return {
            'category': self.category,
            'reward_rate': self.reward_rate,
            'monthly_cap': self.monthly_cap,
            'description': self.description
        }


@dataclass
class CreditCard:
    bank: str
    name: str
    card_type: str  # VISA, MASTERCARD, AMEX
    annual_fee: float = 0.0
    base_reward_rate: float = 0.01
    signup_bonus: Optional[Dict[str, Any]] = None
    image_url: Optional[str] = None
    apply_url: Optional[str] = None
    no_fx_fee: bool = False
    reward_rules: List[RewardRule] = field(default_factory=list)
    source: str = ""  # Which website the data came from
    scraped_at: str = ""

    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.now().isoformat()

    def get_hash(self) -> str:
        """Generate a hash for deduplication"""
        key = f"{self.bank}|{self.name}".lower()
        return hashlib.md5(key.encode()).hexdigest()[:12]

    def to_dict(self) -> dict:
        return {
            'bank': self.bank,
            'name': self.name,
            'card_type': self.card_type,
            'annual_fee': self.annual_fee,
            'base_reward_rate': self.base_reward_rate,
            'signup_bonus': self.signup_bonus,
            'image_url': self.image_url,
            'apply_url': self.apply_url,
            'no_fx_fee': self.no_fx_fee,
            'reward_rules': [r.to_dict() for r in self.reward_rules],
            'source': self.source,
            'scraped_at': self.scraped_at
        }


# ============================================
# Helper Functions
# ============================================

def normalize_bank_name(name: str) -> str:
    """Normalize bank name to standard format"""
    name_lower = name.lower().strip()
    for alias, standard in BANK_ALIASES.items():
        if alias in name_lower:
            return standard
    return name.strip()


def detect_card_type(card_name: str, bank: str) -> str:
    """Detect card type from name"""
    name_lower = card_name.lower()
    bank_lower = bank.lower()

    for card_type, patterns in CARD_TYPE_PATTERNS.items():
        for pattern in patterns:
            if pattern in name_lower or pattern in bank_lower:
                return card_type

    # Default based on bank
    if 'amex' in bank_lower or 'american express' in bank_lower:
        return 'AMEX'

    return 'VISA'  # Default


def parse_percentage(text: str) -> Optional[float]:
    """Parse percentage from text like '5%' or '5x' to decimal"""
    if not text:
        return None

    # Match patterns like "5%", "5.5%", "5x", "5X"
    match = re.search(r'(\d+\.?\d*)\s*[%xX]', text)
    if match:
        value = float(match.group(1))
        # If it's "x" points, assume 1x = 1%
        if 'x' in text.lower():
            return value / 100
        return value / 100

    return None


def parse_annual_fee(text: str) -> float:
    """Parse annual fee from text"""
    if not text:
        return 0.0

    text_lower = text.lower()
    if 'no annual fee' in text_lower or 'no fee' in text_lower or '$0' in text:
        return 0.0

    # Match patterns like "$120", "$120.00", "$120/year"
    match = re.search(r'\$(\d+\.?\d*)', text)
    if match:
        return float(match.group(1))

    return 0.0


def parse_monthly_cap(text: str) -> Optional[float]:
    """Parse monthly spending cap from text"""
    if not text:
        return None

    # Match patterns like "$2,500/month", "up to $2500", "$30,000/year"
    match = re.search(r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:/|per)?\s*(month|year)?', text, re.IGNORECASE)
    if match:
        amount = float(match.group(1).replace(',', ''))
        period = match.group(2)
        if period and 'year' in period.lower():
            return amount / 12  # Convert to monthly
        return amount

    return None


def categorize_reward(description: str) -> str:
    """Determine category from reward description"""
    desc_lower = description.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in desc_lower:
                return category

    return 'OTHER'


# ============================================
# Scrapers
# ============================================

class BaseScraper:
    """Base class for scrapers"""

    def __init__(self, use_selenium: bool = True):
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.driver = None

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
        options.add_argument(f'user-agent={HEADERS["User-Agent"]}')

        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_page_load_timeout(30)
        except Exception as e:
            print(f"Failed to initialize Chrome driver: {e}")
            print("Trying with default settings...")
            try:
                self.driver = webdriver.Chrome()
            except Exception as e2:
                print(f"Chrome driver not available: {e2}")
                self.use_selenium = False

    def close_driver(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def get_page(self, url: str, wait_selector: str = None) -> Optional[str]:
        """Get page content"""
        if self.use_selenium and self.driver:
            try:
                self.driver.get(url)
                if wait_selector:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
                    )
                time.sleep(2)  # Additional wait for dynamic content
                return self.driver.page_source
            except TimeoutException:
                print(f"Timeout loading {url}")
                return None
        else:
            try:
                response = requests.get(url, headers=HEADERS, timeout=30)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                print(f"Request failed for {url}: {e}")
                return None

    def scrape(self) -> List[CreditCard]:
        """Override in subclass"""
        raise NotImplementedError


class CreditCardGeniusScraper(BaseScraper):
    """Scraper for Credit Card Genius"""

    BASE_URL = "https://creditcardgenius.ca"

    CARD_PAGES = [
        "/best-credit-cards/cash-back",
        "/best-credit-cards/rewards",
        "/best-credit-cards/travel",
        "/best-credit-cards/no-fee",
        "/best-credit-cards/low-interest",
    ]

    def scrape(self) -> List[CreditCard]:
        """Scrape all cards from Credit Card Genius"""
        cards = []
        seen_hashes = set()

        if self.use_selenium:
            self.init_driver()

        try:
            for page_path in self.CARD_PAGES:
                url = f"{self.BASE_URL}{page_path}"
                print(f"Scraping: {url}")

                page_cards = self._scrape_page(url)

                for card in page_cards:
                    card_hash = card.get_hash()
                    if card_hash not in seen_hashes:
                        seen_hashes.add(card_hash)
                        cards.append(card)
                        print(f"  Found: {card.bank} {card.name}")

                time.sleep(2)  # Rate limiting

        finally:
            self.close_driver()

        return cards

    def _scrape_page(self, url: str) -> List[CreditCard]:
        """Scrape a single page"""
        cards = []
        html = self.get_page(url, wait_selector=".card-item, .credit-card, [class*='card']")

        if not html:
            return cards

        soup = BeautifulSoup(html, 'lxml')

        # Try multiple selectors for card containers
        card_selectors = [
            'div[class*="card-item"]',
            'div[class*="credit-card"]',
            'article[class*="card"]',
            'div[class*="product-card"]',
            'div[class*="CardItem"]',
        ]

        card_elements = []
        for selector in card_selectors:
            elements = soup.select(selector)
            if elements:
                card_elements = elements
                break

        for element in card_elements:
            card = self._parse_card_element(element)
            if card:
                card.source = "creditcardgenius.ca"
                cards.append(card)

        return cards

    def _parse_card_element(self, element) -> Optional[CreditCard]:
        """Parse a single card element"""
        try:
            # Extract card name
            name_elem = element.select_one('h2, h3, h4, [class*="card-name"], [class*="title"]')
            if not name_elem:
                return None

            full_name = name_elem.get_text(strip=True)
            if not full_name or len(full_name) < 3:
                return None

            # Parse bank and card name
            bank, name = self._parse_card_name(full_name)

            # Extract annual fee
            fee_elem = element.select_one('[class*="fee"], [class*="annual"]')
            annual_fee = 0.0
            if fee_elem:
                annual_fee = parse_annual_fee(fee_elem.get_text())

            # Extract apply URL
            apply_url = None
            link_elem = element.select_one('a[href*="apply"], a[class*="apply"], a[href*="redirect"]')
            if link_elem and link_elem.get('href'):
                apply_url = link_elem['href']
                if not apply_url.startswith('http'):
                    apply_url = f"{self.BASE_URL}{apply_url}"

            # Extract image URL
            image_url = None
            img_elem = element.select_one('img[src*="card"], img[class*="card"]')
            if img_elem and img_elem.get('src'):
                image_url = img_elem['src']
                if not image_url.startswith('http'):
                    image_url = f"{self.BASE_URL}{image_url}"

            # Extract reward rates
            reward_rules = self._parse_rewards(element)

            # Determine base rate
            base_rate = 0.01
            if reward_rules:
                other_rules = [r for r in reward_rules if r.category == 'OTHER']
                if other_rules:
                    base_rate = other_rules[0].reward_rate

            # Check for no FX fee
            text = element.get_text().lower()
            no_fx_fee = 'no foreign' in text or 'no fx' in text or 'no currency' in text

            card = CreditCard(
                bank=bank,
                name=name,
                card_type=detect_card_type(full_name, bank),
                annual_fee=annual_fee,
                base_reward_rate=base_rate,
                apply_url=apply_url,
                image_url=image_url,
                no_fx_fee=no_fx_fee,
                reward_rules=reward_rules
            )

            return card

        except Exception as e:
            print(f"Error parsing card element: {e}")
            return None

    def _parse_card_name(self, full_name: str) -> tuple:
        """Parse full card name into bank and card name"""
        # Common patterns: "TD Cash Back Visa Infinite", "AMEX Cobalt Card"

        # Try to identify bank first
        full_lower = full_name.lower()

        for alias, standard_bank in BANK_ALIASES.items():
            if alias in full_lower:
                # Remove bank name from card name
                pattern = re.compile(re.escape(alias), re.IGNORECASE)
                card_name = pattern.sub('', full_name).strip()
                # Clean up card name
                card_name = re.sub(r'^[\s\-–—]+', '', card_name)
                card_name = re.sub(r'[\s\-–—]+$', '', card_name)
                return standard_bank, card_name if card_name else full_name

        # If no bank found, try splitting by common separators
        parts = re.split(r'\s+[-–—]\s+|\s{2,}', full_name, maxsplit=1)
        if len(parts) == 2:
            return normalize_bank_name(parts[0]), parts[1]

        return "Unknown", full_name

    def _parse_rewards(self, element) -> List[RewardRule]:
        """Parse reward rules from element"""
        rules = []

        # Look for reward rate text
        reward_elems = element.select('[class*="reward"], [class*="rate"], [class*="earn"], li')

        for elem in reward_elems:
            text = elem.get_text(strip=True)
            rate = parse_percentage(text)

            if rate:
                category = categorize_reward(text)
                cap = parse_monthly_cap(text)

                rule = RewardRule(
                    category=category,
                    reward_rate=rate,
                    monthly_cap=cap,
                    description=text[:255]  # Truncate to DB limit
                )
                rules.append(rule)

        return rules


class RatehubScraper(BaseScraper):
    """Scraper for Ratehub.ca"""

    BASE_URL = "https://www.ratehub.ca"

    CARD_PAGES = [
        "/credit-cards/cash-back",
        "/credit-cards/rewards",
        "/credit-cards/travel",
        "/credit-cards/no-fee",
    ]

    def scrape(self) -> List[CreditCard]:
        """Scrape all cards from Ratehub"""
        cards = []
        seen_hashes = set()

        if self.use_selenium:
            self.init_driver()

        try:
            for page_path in self.CARD_PAGES:
                url = f"{self.BASE_URL}{page_path}"
                print(f"Scraping: {url}")

                page_cards = self._scrape_page(url)

                for card in page_cards:
                    card_hash = card.get_hash()
                    if card_hash not in seen_hashes:
                        seen_hashes.add(card_hash)
                        cards.append(card)
                        print(f"  Found: {card.bank} {card.name}")

                time.sleep(2)

        finally:
            self.close_driver()

        return cards

    def _scrape_page(self, url: str) -> List[CreditCard]:
        """Scrape a single page"""
        cards = []
        html = self.get_page(url, wait_selector="[class*='card'], [class*='Card']")

        if not html:
            return cards

        soup = BeautifulSoup(html, 'lxml')

        # Similar parsing logic to CreditCardGenius
        card_selectors = [
            'div[class*="CardProduct"]',
            'div[class*="card-product"]',
            'article[class*="card"]',
            'div[class*="ProductCard"]',
        ]

        card_elements = []
        for selector in card_selectors:
            elements = soup.select(selector)
            if elements:
                card_elements = elements
                break

        for element in card_elements:
            card = self._parse_card_element(element)
            if card:
                card.source = "ratehub.ca"
                cards.append(card)

        return cards

    def _parse_card_element(self, element) -> Optional[CreditCard]:
        """Parse similar to CreditCardGenius"""
        # Implementation similar to CreditCardGeniusScraper._parse_card_element
        # Adjusted for Ratehub's specific HTML structure
        try:
            name_elem = element.select_one('h2, h3, h4, [class*="name"], [class*="title"]')
            if not name_elem:
                return None

            full_name = name_elem.get_text(strip=True)
            if not full_name or len(full_name) < 3:
                return None

            bank, name = self._parse_card_name(full_name)

            fee_elem = element.select_one('[class*="fee"]')
            annual_fee = parse_annual_fee(fee_elem.get_text() if fee_elem else "")

            apply_url = None
            link_elem = element.select_one('a[href]')
            if link_elem:
                href = link_elem.get('href', '')
                if href and not href.startswith('#'):
                    apply_url = href if href.startswith('http') else f"{self.BASE_URL}{href}"

            card = CreditCard(
                bank=bank,
                name=name,
                card_type=detect_card_type(full_name, bank),
                annual_fee=annual_fee,
                base_reward_rate=0.01,
                apply_url=apply_url,
            )

            return card

        except Exception as e:
            return None

    def _parse_card_name(self, full_name: str) -> tuple:
        """Same as CreditCardGeniusScraper"""
        full_lower = full_name.lower()

        for alias, standard_bank in BANK_ALIASES.items():
            if alias in full_lower:
                pattern = re.compile(re.escape(alias), re.IGNORECASE)
                card_name = pattern.sub('', full_name).strip()
                card_name = re.sub(r'^[\s\-–—]+', '', card_name)
                card_name = re.sub(r'[\s\-–—]+$', '', card_name)
                return standard_bank, card_name if card_name else full_name

        return "Unknown", full_name


# ============================================
# SQL Generator
# ============================================

class SQLGenerator:
    """Generate incremental SQL statements"""

    def __init__(self, cards: List[CreditCard], existing_cards: List[Dict] = None):
        self.cards = cards
        self.existing_cards = existing_cards or []
        self.existing_map = {
            f"{c['bank'].lower()}|{c['name'].lower()}": c
            for c in self.existing_cards
        }

    def generate_incremental_sql(self) -> str:
        """Generate SQL for new and updated cards"""
        lines = []
        lines.append(f"-- SaveVia Credit Card Data Update")
        lines.append(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"-- Cards processed: {len(self.cards)}")
        lines.append("")

        new_cards = []
        updated_cards = []

        for card in self.cards:
            key = f"{card.bank.lower()}|{card.name.lower()}"
            if key in self.existing_map:
                # Check if update needed
                existing = self.existing_map[key]
                if self._needs_update(card, existing):
                    updated_cards.append((card, existing))
            else:
                new_cards.append(card)

        # Generate INSERT for new cards
        if new_cards:
            lines.append("-- ============================================")
            lines.append("-- NEW CARDS")
            lines.append("-- ============================================")
            lines.append("")

            for card in new_cards:
                lines.append(self._generate_insert(card))
                lines.append("")

        # Generate UPDATE for changed cards
        if updated_cards:
            lines.append("-- ============================================")
            lines.append("-- UPDATED CARDS")
            lines.append("-- ============================================")
            lines.append("")

            for card, existing in updated_cards:
                lines.append(self._generate_update(card, existing))
                lines.append("")

        if not new_cards and not updated_cards:
            lines.append("-- No changes detected")

        return "\n".join(lines)

    def _needs_update(self, card: CreditCard, existing: Dict) -> bool:
        """Check if card data has changed"""
        if card.annual_fee != existing.get('annual_fee', 0):
            return True
        if card.apply_url and card.apply_url != existing.get('apply_url'):
            return True
        return False

    def _generate_insert(self, card: CreditCard) -> str:
        """Generate INSERT statement for a card"""
        name = card.name.replace("'", "''")
        bank = card.bank.replace("'", "''")

        signup_json = f"'{json.dumps(card.signup_bonus)}'" if card.signup_bonus else "NULL"
        image_url = f"'{card.image_url}'" if card.image_url else "NULL"
        apply_url = f"'{card.apply_url}'" if card.apply_url else "NULL"

        sql = f"""-- {card.bank} {card.name}
INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('{bank}', '{name}', '{card.card_type}', {card.annual_fee}, {card.base_reward_rate}, {signup_json}, {image_url}, {apply_url}, {str(card.no_fx_fee).lower()}, true);

-- Get the card ID for reward rules
SET @card_id = LAST_INSERT_ID();
"""

        # Generate reward rules
        for rule in card.reward_rules:
            desc = rule.description.replace("'", "''")
            cap = str(rule.monthly_cap) if rule.monthly_cap else "NULL"
            sql += f"""
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(@card_id, '{rule.category}', {rule.reward_rate}, {cap}, '{desc}');"""

        return sql

    def _generate_update(self, card: CreditCard, existing: Dict) -> str:
        """Generate UPDATE statement for a card"""
        card_id = existing.get('id', '?')
        updates = []

        if card.annual_fee != existing.get('annual_fee'):
            updates.append(f"annual_fee = {card.annual_fee}")
        if card.apply_url and card.apply_url != existing.get('apply_url'):
            updates.append(f"apply_url = '{card.apply_url}'")
        if card.image_url and card.image_url != existing.get('image_url'):
            updates.append(f"image_url = '{card.image_url}'")

        if not updates:
            return f"-- No changes for {card.bank} {card.name}"

        sql = f"""-- Update {card.bank} {card.name}
UPDATE credit_cards SET
    {', '.join(updates)},
    updated_at = NOW()
WHERE id = {card_id};  -- OR: WHERE bank = '{card.bank}' AND name = '{card.name}'
"""
        return sql


# ============================================
# Main
# ============================================

def load_existing_cards(db_export_path: str = None) -> List[Dict]:
    """Load existing cards from database export or hardcoded list"""
    # This would ideally connect to the database or read from an export
    # For now, return empty list
    return []


def main():
    parser = argparse.ArgumentParser(description='Scrape Canadian credit card data')
    parser.add_argument('--dry-run', action='store_true', help='Print results without saving')
    parser.add_argument('--output', '-o', default='incremental_cards.sql', help='Output SQL file')
    parser.add_argument('--json', '-j', help='Also save as JSON file')
    parser.add_argument('--no-selenium', action='store_true', help='Use requests only (limited)')
    parser.add_argument('--source', choices=['all', 'ccgenius', 'ratehub'], default='all', help='Data source')
    args = parser.parse_args()

    print("=" * 60)
    print("Canadian Credit Card Scraper")
    print("=" * 60)
    print()

    all_cards = []
    use_selenium = not args.no_selenium

    # Scrape Credit Card Genius
    if args.source in ['all', 'ccgenius']:
        print("Scraping Credit Card Genius...")
        try:
            scraper = CreditCardGeniusScraper(use_selenium=use_selenium)
            cards = scraper.scrape()
            all_cards.extend(cards)
            print(f"Found {len(cards)} cards from Credit Card Genius")
        except Exception as e:
            print(f"Error scraping Credit Card Genius: {e}")

    # Scrape Ratehub
    if args.source in ['all', 'ratehub']:
        print("\nScraping Ratehub...")
        try:
            scraper = RatehubScraper(use_selenium=use_selenium)
            cards = scraper.scrape()
            all_cards.extend(cards)
            print(f"Found {len(cards)} cards from Ratehub")
        except Exception as e:
            print(f"Error scraping Ratehub: {e}")

    # Deduplicate
    seen = set()
    unique_cards = []
    for card in all_cards:
        h = card.get_hash()
        if h not in seen:
            seen.add(h)
            unique_cards.append(card)

    print(f"\nTotal unique cards: {len(unique_cards)}")

    if args.dry_run:
        print("\n[DRY RUN] Would generate SQL for:")
        for card in unique_cards:
            print(f"  - {card.bank} {card.name} (${card.annual_fee}/yr)")
        return

    # Load existing cards for comparison
    existing_cards = load_existing_cards()

    # Generate SQL
    generator = SQLGenerator(unique_cards, existing_cards)
    sql = generator.generate_incremental_sql()

    # Save SQL
    output_path = f"/Users/aisenyc/savevia/scripts/scraper/{args.output}"
    with open(output_path, 'w') as f:
        f.write(sql)
    print(f"\nSQL saved to: {output_path}")

    # Save JSON if requested
    if args.json:
        json_path = f"/Users/aisenyc/savevia/scripts/scraper/{args.json}"
        with open(json_path, 'w') as f:
            json.dump([c.to_dict() for c in unique_cards], f, indent=2)
        print(f"JSON saved to: {json_path}")

    print("\nDone!")


if __name__ == "__main__":
    main()
