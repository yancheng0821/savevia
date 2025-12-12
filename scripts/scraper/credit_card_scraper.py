#!/usr/bin/env python3
"""
Canadian Credit Card Data Scraper
Scrapes credit card information from Rewards Canada and generates SQL statements.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from decimal import Decimal
import time

# Headers to mimic browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

# Spending categories matching the backend enum
CATEGORIES = [
    'DINING', 'GROCERY', 'GAS', 'TRAVEL', 'STREAMING', 'TRANSIT',
    'PHARMACY', 'RENT', 'RECURRING', 'ONLINE_SHOPPING', 'FOREIGN',
    'RETAIL', 'ENTERTAINMENT', 'PERSONAL_SERVICES', 'HOME_IMPROVEMENT',
    'WHOLESALE', 'INSURANCE', 'TELECOM', 'EV_CHARGING', 'OTHER'
]

@dataclass
class RewardRule:
    category: str
    reward_rate: Decimal
    monthly_cap: Optional[Decimal] = None
    description: str = ""

@dataclass
class CreditCard:
    bank: str
    name: str
    card_type: str  # VISA, MASTERCARD, AMEX
    annual_fee: Decimal
    base_reward_rate: Decimal
    signup_bonus_json: Optional[str] = None
    image_url: Optional[str] = None
    apply_url: Optional[str] = None
    no_fx_fee: bool = False
    reward_rules: List[RewardRule] = field(default_factory=list)


def scrape_rewards_canada_travel():
    """Scrape travel rewards cards from Rewards Canada"""
    url = "https://www.rewardscanada.ca/TopTravelCreditCard/"
    cards = []

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        # Find card containers - structure varies by page
        # This is a template - actual selectors need to be adjusted based on page structure
        card_divs = soup.find_all('div', class_=re.compile(r'card|credit'))

        for div in card_divs:
            # Extract card details - selectors need adjustment
            name_elem = div.find(['h2', 'h3', 'h4'], class_=re.compile(r'card-name|title'))
            if name_elem:
                print(f"Found card: {name_elem.text.strip()}")

    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")

    return cards


def scrape_rewards_canada_cashback():
    """Scrape cash back cards from Rewards Canada"""
    url = "https://www.rewardscanada.ca/topcashback/"
    cards = []

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        # Find card containers
        card_divs = soup.find_all('div', class_=re.compile(r'card|credit'))

        for div in card_divs:
            name_elem = div.find(['h2', 'h3', 'h4'], class_=re.compile(r'card-name|title'))
            if name_elem:
                print(f"Found card: {name_elem.text.strip()}")

    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")

    return cards


def generate_sql_insert(card: CreditCard, card_id: int) -> str:
    """Generate SQL INSERT statement for a credit card"""

    # Escape single quotes in strings
    name = card.name.replace("'", "''")
    bank = card.bank.replace("'", "''")

    signup_bonus = f"'{card.signup_bonus_json}'" if card.signup_bonus_json else "NULL"
    image_url = f"'{card.image_url}'" if card.image_url else "NULL"
    apply_url = f"'{card.apply_url}'" if card.apply_url else "NULL"

    sql = f"""INSERT INTO credit_cards (bank, name, card_type, annual_fee, base_reward_rate, signup_bonus_json, image_url, apply_url, no_fx_fee, is_active) VALUES
('{bank}', '{name}', '{card.card_type}', {card.annual_fee}, {card.base_reward_rate}, {signup_bonus}, {image_url}, {apply_url}, {str(card.no_fx_fee).lower()}, true);
"""

    # Generate reward rules
    for rule in card.reward_rules:
        desc = rule.description.replace("'", "''")
        monthly_cap = str(rule.monthly_cap) if rule.monthly_cap else "NULL"
        sql += f"""INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
({card_id}, '{rule.category}', {rule.reward_rate}, {monthly_cap}, '{desc}');
"""

    return sql


# Pre-defined card data based on research
# This data is manually curated from Rewards Canada and other sources
KNOWN_CARDS = [
    # ============================================
    # Cards that may be missing or need updates
    # ============================================

    CreditCard(
        bank="Scotiabank",
        name="Passport Visa Infinite",
        card_type="VISA",
        annual_fee=Decimal("150.00"),
        base_reward_rate=Decimal("0.01"),
        signup_bonus_json='{"bonusAmount": 45000, "minSpend": 1000, "daysToComplete": 90, "description": "Up to 45,000 Scene+ points + 10,000 annual bonus at $40K spend"}',
        apply_url="https://www.scotiabank.com/ca/en/personal/credit-cards/visa/passport-infinite-card.html",
        no_fx_fee=True,
        reward_rules=[
            RewardRule("GROCERY", Decimal("0.03"), None, "3x Scene+ points at Empire stores (Sobeys/Safeway/IGA)"),
            RewardRule("DINING", Decimal("0.02"), None, "2x Scene+ points on dining"),
            RewardRule("TRANSIT", Decimal("0.02"), None, "2x Scene+ points on transit"),
            RewardRule("ENTERTAINMENT", Decimal("0.02"), None, "2x Scene+ points on entertainment"),
            RewardRule("FOREIGN", Decimal("0.01"), None, "No FX fee on foreign purchases"),
        ]
    ),

    CreditCard(
        bank="Rogers",
        name="World Elite Mastercard",
        card_type="MASTERCARD",
        annual_fee=Decimal("0"),
        base_reward_rate=Decimal("0.015"),
        signup_bonus_json='{"bonusAmount": 25, "minSpend": 500, "daysToComplete": 90, "description": "$25 bonus on first $500 spent"}',
        apply_url="https://www.rogersbank.com/en/rogers_world_elite_mastercard",
        no_fx_fee=False,
        reward_rules=[
            RewardRule("FOREIGN", Decimal("0.03"), None, "3% on U.S. dollar purchases"),
            RewardRule("TELECOM", Decimal("0.03"), None, "3% on Rogers/Fido/Shaw services"),
        ]
    ),

    CreditCard(
        bank="Neo",
        name="World Elite Mastercard",
        card_type="MASTERCARD",
        annual_fee=Decimal("125.00"),
        base_reward_rate=Decimal("0.01"),
        signup_bonus_json='{"bonusAmount": 50, "minSpend": 500, "daysToComplete": 90, "description": "$50 welcome bonus"}',
        apply_url="https://www.neofinancial.com/credit",
        no_fx_fee=False,
        reward_rules=[
            RewardRule("GROCERY", Decimal("0.05"), Decimal("1000"), "5% on groceries (up to $1,000/month)"),
            RewardRule("RECURRING", Decimal("0.04"), Decimal("1000"), "4% on recurring bills (up to $1,000/month)"),
            RewardRule("GAS", Decimal("0.03"), Decimal("1000"), "3% on gas (up to $1,000/month)"),
            RewardRule("EV_CHARGING", Decimal("0.03"), Decimal("1000"), "3% on EV charging (up to $1,000/month)"),
            RewardRule("TELECOM", Decimal("0.04"), Decimal("1000"), "4% on telecom/internet (up to $1,000/month)"),
            RewardRule("INSURANCE", Decimal("0.04"), Decimal("1000"), "4% on insurance (up to $1,000/month)"),
            RewardRule("STREAMING", Decimal("0.04"), Decimal("1000"), "4% on streaming (up to $1,000/month)"),
        ]
    ),

    CreditCard(
        bank="CIBC",
        name="Dividend Visa Infinite",
        card_type="VISA",
        annual_fee=Decimal("120.00"),
        base_reward_rate=Decimal("0.01"),
        signup_bonus_json='{"bonusAmount": 300, "minSpend": 3000, "daysToComplete": 120, "description": "10% cashback first 4 statements up to $3,000"}',
        apply_url="https://www.cibc.com/en/personal-banking/credit-cards/all-credit-cards/dividend-visa-infinite-card.html",
        no_fx_fee=False,
        reward_rules=[
            RewardRule("GROCERY", Decimal("0.04"), Decimal("1667"), "4% on groceries (up to $20,000/year)"),
            RewardRule("GAS", Decimal("0.04"), Decimal("1667"), "4% on gas (up to $20,000/year)"),
            RewardRule("EV_CHARGING", Decimal("0.04"), Decimal("1667"), "4% on EV charging (up to $20,000/year)"),
            RewardRule("TRANSIT", Decimal("0.02"), Decimal("1667"), "2% on transit (up to $20,000/year)"),
            RewardRule("DINING", Decimal("0.02"), Decimal("1667"), "2% on dining (up to $20,000/year)"),
            RewardRule("RECURRING", Decimal("0.02"), Decimal("1667"), "2% on recurring bills (up to $20,000/year)"),
            RewardRule("TELECOM", Decimal("0.02"), Decimal("1667"), "2% on telecom (up to $20,000/year)"),
            RewardRule("STREAMING", Decimal("0.02"), Decimal("1667"), "2% on streaming (up to $20,000/year)"),
        ]
    ),

    CreditCard(
        bank="Simplii",
        name="Cash Back Visa Card",
        card_type="VISA",
        annual_fee=Decimal("0"),
        base_reward_rate=Decimal("0.005"),
        signup_bonus_json='{"bonusAmount": 400, "minSpend": 5000, "daysToComplete": 120, "description": "$400 + 8% cashback on restaurants first 3 months"}',
        apply_url="https://www.simplii.com/en/credit-cards/cash-back-visa.html",
        no_fx_fee=False,
        reward_rules=[
            RewardRule("DINING", Decimal("0.04"), Decimal("417"), "4% on restaurants (up to $5,000/year)"),
            RewardRule("GROCERY", Decimal("0.015"), Decimal("1250"), "1.5% on groceries (up to $15,000/year)"),
            RewardRule("GAS", Decimal("0.015"), Decimal("1250"), "1.5% on gas (up to $15,000/year)"),
            RewardRule("PHARMACY", Decimal("0.015"), Decimal("1250"), "1.5% on pharmacies (up to $15,000/year)"),
            RewardRule("RECURRING", Decimal("0.015"), Decimal("1250"), "1.5% on pre-authorized payments (up to $15,000/year)"),
        ]
    ),

    CreditCard(
        bank="Tangerine",
        name="Money-Back Credit Card",
        card_type="MASTERCARD",
        annual_fee=Decimal("0"),
        base_reward_rate=Decimal("0.005"),
        signup_bonus_json='{"bonusAmount": 100, "minSpend": 1000, "daysToComplete": 60, "description": "10% cashback first 2 months up to $1,000"}',
        apply_url="https://www.tangerine.ca/en/products/spending/creditcard/money-back",
        no_fx_fee=False,
        reward_rules=[
            # User can select 2-3 categories at 2%
            RewardRule("GROCERY", Decimal("0.02"), None, "2% on groceries (if selected as bonus category)"),
            RewardRule("GAS", Decimal("0.02"), None, "2% on gas (if selected as bonus category)"),
            RewardRule("DINING", Decimal("0.02"), None, "2% on dining (if selected as bonus category)"),
            RewardRule("RECURRING", Decimal("0.02"), None, "2% on recurring bills (if selected as bonus category)"),
            RewardRule("PHARMACY", Decimal("0.02"), None, "2% on pharmacy (if selected as bonus category)"),
            RewardRule("ENTERTAINMENT", Decimal("0.02"), None, "2% on entertainment (if selected as bonus category)"),
            RewardRule("HOME_IMPROVEMENT", Decimal("0.02"), None, "2% on home improvement (if selected as bonus category)"),
            RewardRule("TRANSIT", Decimal("0.02"), None, "2% on public transit (if selected as bonus category)"),
        ]
    ),

    CreditCard(
        bank="BMO",
        name="CashBack World Elite Mastercard",
        card_type="MASTERCARD",
        annual_fee=Decimal("120.00"),
        base_reward_rate=Decimal("0.015"),
        signup_bonus_json='{"bonusAmount": 335, "minSpend": 3000, "daysToComplete": 90, "description": "10% cashback first 3 months + $120 fee waived year 1"}',
        apply_url="https://www.bmo.com/main/personal/credit-cards/bmo-cashback-world-elite-mastercard/",
        no_fx_fee=False,
        reward_rules=[
            RewardRule("GROCERY", Decimal("0.05"), Decimal("500"), "5% on groceries (up to $500/month)"),
            RewardRule("TRANSIT", Decimal("0.04"), Decimal("300"), "4% on transit (up to $300/month)"),
            RewardRule("GAS", Decimal("0.03"), Decimal("300"), "3% on gas (up to $300/month)"),
            RewardRule("EV_CHARGING", Decimal("0.03"), Decimal("300"), "3% on EV charging (up to $300/month)"),
            RewardRule("RECURRING", Decimal("0.02"), Decimal("500"), "2% on recurring bills (up to $500/month)"),
            RewardRule("TELECOM", Decimal("0.02"), Decimal("500"), "2% on telecom (up to $500/month)"),
            RewardRule("STREAMING", Decimal("0.02"), Decimal("500"), "2% on streaming (up to $500/month)"),
        ]
    ),

    CreditCard(
        bank="AMEX",
        name="Cobalt Card",
        card_type="AMEX",
        annual_fee=Decimal("191.88"),
        base_reward_rate=Decimal("0.01"),
        signup_bonus_json='{"bonusAmount": 15000, "minSpend": 750, "daysToComplete": 30, "description": "1,250 MR points/month when spending $750+, for 12 months"}',
        apply_url="https://www.americanexpress.com/ca/en/credit-cards/cobalt-card/",
        no_fx_fee=False,
        reward_rules=[
            RewardRule("DINING", Decimal("0.05"), Decimal("2500"), "5x points on dining (up to $2,500/month)"),
            RewardRule("GROCERY", Decimal("0.05"), Decimal("2500"), "5x points on groceries (up to $2,500/month)"),
            RewardRule("STREAMING", Decimal("0.03"), None, "3x points on streaming"),
            RewardRule("TRAVEL", Decimal("0.02"), None, "2x points on travel"),
            RewardRule("TRANSIT", Decimal("0.02"), None, "2x points on transit & rideshare"),
            RewardRule("GAS", Decimal("0.02"), None, "2x points on gas"),
            RewardRule("ENTERTAINMENT", Decimal("0.02"), None, "2x points on entertainment"),
            RewardRule("PERSONAL_SERVICES", Decimal("0.05"), Decimal("2500"), "5x points on personal services (beauty, spa)"),
        ]
    ),

    CreditCard(
        bank="TD",
        name="Cash Back Visa Infinite",
        card_type="VISA",
        annual_fee=Decimal("139.00"),
        base_reward_rate=Decimal("0.01"),
        signup_bonus_json='{"bonusAmount": 350, "minSpend": 3500, "daysToComplete": 90, "description": "10% cashback first 3 months on bonus categories"}',
        apply_url="https://www.td.com/ca/en/personal-banking/products/credit-cards/cash-back/cash-back-visa-infinite-card",
        no_fx_fee=False,
        reward_rules=[
            RewardRule("GROCERY", Decimal("0.03"), Decimal("1250"), "3% on groceries (up to $15,000/year)"),
            RewardRule("GAS", Decimal("0.03"), Decimal("1250"), "3% on gas (up to $15,000/year)"),
            RewardRule("EV_CHARGING", Decimal("0.03"), Decimal("1250"), "3% on EV charging (up to $15,000/year)"),
            RewardRule("TRANSIT", Decimal("0.03"), Decimal("1250"), "3% on transit (up to $15,000/year)"),
            RewardRule("RECURRING", Decimal("0.03"), Decimal("1250"), "3% on recurring bills (up to $15,000/year)"),
            RewardRule("STREAMING", Decimal("0.03"), Decimal("1250"), "3% on streaming (up to $15,000/year)"),
            RewardRule("TELECOM", Decimal("0.03"), Decimal("1250"), "3% on telecom (up to $15,000/year)"),
        ]
    ),

    CreditCard(
        bank="PC Financial",
        name="World Elite Mastercard",
        card_type="MASTERCARD",
        annual_fee=Decimal("0"),
        base_reward_rate=Decimal("0.01"),
        signup_bonus_json='{"bonusAmount": 20000, "minSpend": 1000, "daysToComplete": 30, "description": "20,000 PC Optimum points"}',
        apply_url="https://www.pcfinancial.ca/en/credit-cards/pc-world-elite-mastercard",
        no_fx_fee=False,
        reward_rules=[
            RewardRule("GROCERY", Decimal("0.03"), None, "30 PC Optimum points per $1 at Loblaw stores (~3%)"),
            RewardRule("PHARMACY", Decimal("0.045"), None, "45 PC Optimum points per $1 at Shoppers (~4.5%)"),
            RewardRule("GAS", Decimal("0.03"), None, "30 PC Optimum points per $1 at Esso/Mobil"),
        ]
    ),

    CreditCard(
        bank="Home Trust",
        name="Preferred Visa",
        card_type="VISA",
        annual_fee=Decimal("0"),
        base_reward_rate=Decimal("0.01"),
        signup_bonus_json=None,
        apply_url="https://www.hometrust.ca/credit-cards/preferred-visa-card/",
        no_fx_fee=True,
        reward_rules=[
            RewardRule("FOREIGN", Decimal("0.01"), None, "1% on all purchases + no FX fee"),
            RewardRule("TRAVEL", Decimal("0.01"), None, "1% on travel with no FX fee"),
        ]
    ),

    CreditCard(
        bank="Marriott Bonvoy",
        name="American Express Card",
        card_type="AMEX",
        annual_fee=Decimal("120.00"),
        base_reward_rate=Decimal("0.02"),
        signup_bonus_json='{"bonusAmount": 50000, "minSpend": 1500, "daysToComplete": 90, "description": "50,000 Marriott points + free night annually"}',
        apply_url="https://www.americanexpress.com/ca/en/credit-cards/marriott-bonvoy/",
        no_fx_fee=False,
        reward_rules=[
            RewardRule("TRAVEL", Decimal("0.05"), None, "5 points per $1 at Marriott hotels"),
            RewardRule("DINING", Decimal("0.02"), None, "2 points per $1 on dining"),
        ]
    ),
]


def generate_update_sql():
    """Generate SQL to update existing cards and add new reward rules for extended categories"""

    sql = """-- SaveVia Extended Categories Update
-- Adds reward rules for new categories: RETAIL, ENTERTAINMENT, PERSONAL_SERVICES,
-- HOME_IMPROVEMENT, WHOLESALE, INSURANCE, TELECOM, EV_CHARGING

-- ============================================
-- Update existing cards with new category rules
-- ============================================

-- AMEX Cobalt (ID 1) - Add ENTERTAINMENT and PERSONAL_SERVICES
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(1, 'ENTERTAINMENT', 0.02, NULL, '2x points on entertainment')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(1, 'PERSONAL_SERVICES', 0.05, 2500, '5x points on personal services (beauty, spa)')
ON DUPLICATE KEY UPDATE reward_rate = 0.05;

-- TD Cash Back Visa Infinite (ID 8) - Add EV_CHARGING and TELECOM
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(8, 'EV_CHARGING', 0.03, 1250, '3% on EV charging (up to $15,000/year)')
ON DUPLICATE KEY UPDATE reward_rate = 0.03;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(8, 'TELECOM', 0.03, 1250, '3% on telecom (up to $15,000/year)')
ON DUPLICATE KEY UPDATE reward_rate = 0.03;

-- Scotiabank Passport (ID 19) - Add ENTERTAINMENT
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(19, 'ENTERTAINMENT', 0.02, NULL, '2x Scene+ points on entertainment')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

-- Scotiabank Momentum (ID 20) - Already has transit, gas - add EV_CHARGING
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(20, 'EV_CHARGING', 0.02, 2083, '2% on EV charging (up to $25,000/year)')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(20, 'TELECOM', 0.04, 2083, '4% on telecom (up to $25,000/year)')
ON DUPLICATE KEY UPDATE reward_rate = 0.04;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(20, 'INSURANCE', 0.04, 2083, '4% on insurance (up to $25,000/year)')
ON DUPLICATE KEY UPDATE reward_rate = 0.04;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(20, 'STREAMING', 0.04, 2083, '4% on streaming (up to $25,000/year)')
ON DUPLICATE KEY UPDATE reward_rate = 0.04;

-- CIBC Dividend Visa Infinite (ID 25) - Add EV_CHARGING, TELECOM, STREAMING
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(25, 'EV_CHARGING', 0.04, 1667, '4% on EV charging (up to $20,000/year)')
ON DUPLICATE KEY UPDATE reward_rate = 0.04;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(25, 'TELECOM', 0.02, 1667, '2% on telecom (up to $20,000/year)')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(25, 'STREAMING', 0.02, 1667, '2% on streaming (up to $20,000/year)')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(25, 'INSURANCE', 0.02, 1667, '2% on insurance (up to $20,000/year)')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

-- BMO CashBack World Elite (ID 28) - Add EV_CHARGING, TELECOM, STREAMING
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(28, 'EV_CHARGING', 0.03, 300, '3% on EV charging (up to $300/month)')
ON DUPLICATE KEY UPDATE reward_rate = 0.03;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(28, 'TELECOM', 0.02, 500, '2% on telecom (up to $500/month)')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(28, 'STREAMING', 0.02, 500, '2% on streaming (up to $500/month)')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

-- Rogers World Elite (ID 31) - Add TELECOM
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(31, 'TELECOM', 0.03, NULL, '3% on Rogers/Fido/Shaw services')
ON DUPLICATE KEY UPDATE reward_rate = 0.03;

-- Neo World Elite (ID 35) - Add EV_CHARGING, TELECOM, INSURANCE, STREAMING
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(35, 'EV_CHARGING', 0.03, NULL, '3% on EV charging')
ON DUPLICATE KEY UPDATE reward_rate = 0.03;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(35, 'TELECOM', 0.04, NULL, '4% on telecom/internet')
ON DUPLICATE KEY UPDATE reward_rate = 0.04;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(35, 'INSURANCE', 0.04, NULL, '4% on insurance')
ON DUPLICATE KEY UPDATE reward_rate = 0.04;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(35, 'STREAMING', 0.04, NULL, '4% on streaming')
ON DUPLICATE KEY UPDATE reward_rate = 0.04;

-- Neo World Mastercard (ID 36) - Add EV_CHARGING, TELECOM
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(36, 'EV_CHARGING', 0.02, NULL, '2% on EV charging')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(36, 'TELECOM', 0.02, NULL, '2% on telecom/internet')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

-- PC Financial World Elite (ID 37) - Add RETAIL (for PC stores)
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(37, 'RETAIL', 0.01, NULL, '10 PC Optimum points per $1 at other retail')
ON DUPLICATE KEY UPDATE reward_rate = 0.01;

-- Simplii Cash Back (ID 39) - Add RECURRING
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(39, 'RECURRING', 0.015, NULL, '1.5% on pre-authorized payments')
ON DUPLICATE KEY UPDATE reward_rate = 0.015;

-- MBNA Rewards World Elite (ID 40) - Already has STREAMING, RECURRING - add TELECOM
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(40, 'TELECOM', 0.05, NULL, '5x points on telecom')
ON DUPLICATE KEY UPDATE reward_rate = 0.05;

-- National Bank World Elite (ID 42) - Add TELECOM, INSURANCE
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(42, 'TELECOM', 0.02, NULL, '2x points on telecom')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(42, 'INSURANCE', 0.02, NULL, '2x points on insurance')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(42, 'STREAMING', 0.02, NULL, '2x points on streaming')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

-- Tangerine Money-Back (ID 33) - Add more selectable categories
INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(33, 'RECURRING', 0.02, NULL, '2% on recurring bills (if selected)')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(33, 'PHARMACY', 0.02, NULL, '2% on pharmacy (if selected)')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(33, 'ENTERTAINMENT', 0.02, NULL, '2% on entertainment (if selected)')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(33, 'HOME_IMPROVEMENT', 0.02, NULL, '2% on home improvement (if selected)')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description) VALUES
(33, 'TRANSIT', 0.02, NULL, '2% on public transit (if selected)')
ON DUPLICATE KEY UPDATE reward_rate = 0.02;

-- ============================================
-- Update no_fx_fee for cards that have it
-- ============================================
UPDATE credit_cards SET no_fx_fee = true WHERE id = 19; -- Scotiabank Passport
UPDATE credit_cards SET no_fx_fee = true WHERE id = 43; -- Home Trust Preferred

"""
    return sql


def main():
    print("Canadian Credit Card Scraper")
    print("=" * 50)

    # Generate SQL for extended categories
    sql = generate_update_sql()

    # Write to file
    output_file = "/Users/aisenyc/savevia/docker/mysql/init/11-extended-category-rules.sql"
    with open(output_file, 'w') as f:
        f.write(sql)

    print(f"\nGenerated SQL file: {output_file}")
    print("\nTo apply, run:")
    print(f"  mysql -u root -p savevia < {output_file}")

    # Also try to scrape live data (may fail due to site structure)
    print("\n" + "=" * 50)
    print("Attempting to scrape live data...")

    try:
        scrape_rewards_canada_travel()
        scrape_rewards_canada_cashback()
    except Exception as e:
        print(f"Scraping failed: {e}")
        print("Using pre-defined card data instead.")


if __name__ == "__main__":
    main()
