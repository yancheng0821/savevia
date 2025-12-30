#!/usr/bin/env python3
"""
Import credit card data from savevia.app API response.

Usage:
    python scripts/import_savevia_data.py

This script loads the sample data from savevia.app API format and saves it to data/cards.json.
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.storage import CardStorage


# Sample data from savevia.app API (this is the data you provided)
SAMPLE_DATA = [
    {
        "id": 6,
        "bank": "AMEX",
        "name": "Aeroplan Card",
        "cardType": "AMEX",
        "annualFee": 120.00,
        "baseRewardRate": 0.0100,
        "imageUrl": '{"gradient": "linear-gradient(135deg, #016fd0 0%, #004080 100%)", "textColor": "white"}',
        "applyUrl": "https://www.americanexpress.com/en-ca/charge-cards/aeroplan-card/",
        "noFxFee": False,
        "signupBonus": {
            "bonusAmount": 30000,
            "minSpend": 1500,
            "daysToComplete": 90,
            "description": None
        },
        "rewardRules": [
            {"id": 13, "category": "TRAVEL", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2x points on Air Canada & travel"},
            {"id": 14, "category": "DINING", "rewardRate": 0.0150, "monthlyCapAmount": None, "description": "1.5x points on dining"},
            {"id": 15, "category": "GROCERY", "rewardRate": 0.0150, "monthlyCapAmount": None, "description": "1.5x points on groceries"}
        ]
    },
    {
        "id": 1,
        "bank": "AMEX",
        "name": "Cobalt Card",
        "cardType": "AMEX",
        "annualFee": 191.88,
        "baseRewardRate": 0.0100,
        "imageUrl": '{"gradient": "linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%)", "textColor": "white"}',
        "applyUrl": "https://www.americanexpress.com/ca/en/credit-cards/cobalt-card/",
        "noFxFee": False,
        "signupBonus": {
            "bonusAmount": 15000,
            "minSpend": 750,
            "daysToComplete": 30,
            "description": "1,250 MR points/month when spending $750+, for 12 months"
        },
        "rewardRules": [
            {"id": 1, "category": "DINING", "rewardRate": 0.0500, "monthlyCapAmount": 2500.00, "description": "5x points on dining (up to $2,500/month)"},
            {"id": 2, "category": "GROCERY", "rewardRate": 0.0500, "monthlyCapAmount": 2500.00, "description": "5x points on groceries (up to $2,500/month)"},
            {"id": 3, "category": "STREAMING", "rewardRate": 0.0300, "monthlyCapAmount": None, "description": "3x points on streaming"},
            {"id": 4, "category": "TRAVEL", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2x points on travel booked via Amex Travel"},
            {"id": 5, "category": "TRANSIT", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2x points on transit & rideshare"},
            {"id": 6, "category": "GAS", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2x points on gas"},
            {"id": 111, "category": "ENTERTAINMENT", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2x points on entertainment"},
            {"id": 112, "category": "PERSONAL_SERVICES", "rewardRate": 0.0500, "monthlyCapAmount": 2500.00, "description": "5x points on personal services (beauty, spa)"},
            {"id": 148, "category": "RETAIL", "rewardRate": 0.0100, "monthlyCapAmount": None, "description": "1x points on retail shopping"},
            {"id": 155, "category": "HOME_IMPROVEMENT", "rewardRate": 0.0100, "monthlyCapAmount": None, "description": "1x points on home improvement"}
        ]
    },
    {
        "id": 2,
        "bank": "AMEX",
        "name": "Gold Rewards Card",
        "cardType": "AMEX",
        "annualFee": 150.00,
        "baseRewardRate": 0.0100,
        "imageUrl": '{"gradient": "linear-gradient(135deg, #c9a227 0%, #9a7b1c 100%)", "textColor": "#1a1a1a"}',
        "applyUrl": "https://www.americanexpress.com/ca/en/credit-cards/gold-rewards-card/",
        "noFxFee": False,
        "signupBonus": {
            "bonusAmount": 40000,
            "minSpend": 3000,
            "daysToComplete": 90,
            "description": None
        },
        "rewardRules": [
            {"id": 7, "category": "TRAVEL", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2x points on travel"},
            {"id": 8, "category": "GAS", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2x points on gas"}
        ]
    },
    {
        "id": 5,
        "bank": "AMEX",
        "name": "SimplyCash",
        "cardType": "AMEX",
        "annualFee": 0.00,
        "baseRewardRate": 0.0125,
        "imageUrl": '{"gradient": "linear-gradient(135deg, #0077b6 0%, #005a8c 100%)", "textColor": "white"}',
        "applyUrl": "https://www.americanexpress.com/ca/en/credit-cards/simply-cash/",
        "noFxFee": False,
        "signupBonus": None,
        "rewardRules": []
    },
    {
        "id": 4,
        "bank": "AMEX",
        "name": "SimplyCash Preferred",
        "cardType": "AMEX",
        "annualFee": 119.88,
        "baseRewardRate": 0.0200,
        "imageUrl": '{"gradient": "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)", "textColor": "white"}',
        "applyUrl": "https://www.americanexpress.com/ca/en/credit-cards/simply-cash-preferred/",
        "noFxFee": False,
        "signupBonus": {
            "bonusAmount": 250,
            "minSpend": 2000,
            "daysToComplete": 90,
            "description": "10% cashback first 3 months up to $2000 + $50 credit in month 13"
        },
        "rewardRules": [
            {"id": 11, "category": "GROCERY", "rewardRate": 0.0400, "monthlyCapAmount": 2500.00, "description": "4% on groceries (up to $30,000/year combined with gas)"},
            {"id": 12, "category": "GAS", "rewardRate": 0.0400, "monthlyCapAmount": 2500.00, "description": "4% on gas (up to $30,000/year combined with grocery)"},
            {"id": 145, "category": "EV_CHARGING", "rewardRate": 0.0400, "monthlyCapAmount": 2500.00, "description": "4% on EV charging (up to $30,000/year combined with gas)"},
            {"id": 149, "category": "RETAIL", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2% on retail shopping"},
            {"id": 156, "category": "HOME_IMPROVEMENT", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2% on home improvement"}
        ]
    },
    {
        "id": 28,
        "bank": "BMO",
        "name": "CashBack World Elite Mastercard",
        "cardType": "MASTERCARD",
        "annualFee": 120.00,
        "baseRewardRate": 0.0150,
        "imageUrl": '{"gradient": "linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%)", "textColor": "white"}',
        "applyUrl": "https://www.bmo.com/en-ca/main/personal/credit-cards/bmo-cashback-world-elite-mastercard/",
        "noFxFee": False,
        "signupBonus": {
            "bonusAmount": 335,
            "minSpend": 3000,
            "daysToComplete": 90,
            "description": "10% cashback first 3 months + $120 fee waived year 1"
        },
        "rewardRules": [
            {"id": 62, "category": "GROCERY", "rewardRate": 0.0500, "monthlyCapAmount": 500.00, "description": "5% on groceries (up to $500/month)"},
            {"id": 63, "category": "TRANSIT", "rewardRate": 0.0400, "monthlyCapAmount": 300.00, "description": "4% on transit (up to $300/month)"},
            {"id": 64, "category": "GAS", "rewardRate": 0.0300, "monthlyCapAmount": 300.00, "description": "3% on gas (up to $300/month)"},
            {"id": 65, "category": "RECURRING", "rewardRate": 0.0200, "monthlyCapAmount": 500.00, "description": "2% on recurring bills (up to $500/month)"}
        ]
    },
    {
        "id": 39,
        "bank": "Simplii",
        "name": "Cash Back Visa Card",
        "cardType": "VISA",
        "annualFee": 0.00,
        "baseRewardRate": 0.0050,
        "imageUrl": '{"gradient": "linear-gradient(135deg, #1a2332 0%, #0f1419 100%)", "textColor": "white"}',
        "applyUrl": "https://www.simplii.com/en/credit-cards/cash-back-visa.html",
        "noFxFee": False,
        "signupBonus": {
            "bonusAmount": 400,
            "minSpend": 5000,
            "daysToComplete": 120,
            "description": "8% dining first 3 months + $200 bonus on $5K spend"
        },
        "rewardRules": [
            {"id": 81, "category": "DINING", "rewardRate": 0.0400, "monthlyCapAmount": None, "description": "4% on restaurants"},
            {"id": 82, "category": "GROCERY", "rewardRate": 0.0150, "monthlyCapAmount": None, "description": "1.5% on groceries"},
            {"id": 83, "category": "GAS", "rewardRate": 0.0150, "monthlyCapAmount": None, "description": "1.5% on gas"},
            {"id": 84, "category": "PHARMACY", "rewardRate": 0.0150, "monthlyCapAmount": None, "description": "1.5% on pharmacies"},
            {"id": 135, "category": "RECURRING", "rewardRate": 0.0150, "monthlyCapAmount": None, "description": "1.5% on pre-authorized payments"}
        ]
    },
    {
        "id": 33,
        "bank": "Tangerine",
        "name": "Money-Back Credit Card",
        "cardType": "MASTERCARD",
        "annualFee": 0.00,
        "baseRewardRate": 0.0050,
        "imageUrl": '{"gradient": "linear-gradient(135deg, #ff6600 0%, #cc5200 100%)", "textColor": "white"}',
        "applyUrl": "https://www.tangerine.ca/en/products/spending/creditcard/money-back",
        "noFxFee": False,
        "signupBonus": {
            "bonusAmount": 100,
            "minSpend": 1000,
            "daysToComplete": 60,
            "description": "10% cashback on first $1,000 in 2 months"
        },
        "rewardRules": [
            {"id": 70, "category": "GROCERY", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2% on groceries (if selected)"},
            {"id": 71, "category": "GAS", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2% on gas (if selected)"},
            {"id": 72, "category": "DINING", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2% on restaurants (if selected)"},
            {"id": 140, "category": "RECURRING", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2% on recurring bills (if selected)"},
            {"id": 141, "category": "PHARMACY", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2% on pharmacy (if selected)"},
            {"id": 142, "category": "ENTERTAINMENT", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2% on entertainment (if selected)"},
            {"id": 143, "category": "HOME_IMPROVEMENT", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2% on home improvement (if selected)"},
            {"id": 144, "category": "TRANSIT", "rewardRate": 0.0200, "monthlyCapAmount": None, "description": "2% on public transit (if selected)"}
        ]
    },
    {
        "id": 8,
        "bank": "TD",
        "name": "Cash Back Visa Infinite",
        "cardType": "VISA",
        "annualFee": 139.00,
        "baseRewardRate": 0.0100,
        "imageUrl": '{"gradient": "linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%)", "textColor": "white"}',
        "applyUrl": "https://www.td.com/ca/en/personal-banking/products/credit-cards/cash-back/cash-back-visa-infinite-card",
        "noFxFee": False,
        "signupBonus": {
            "bonusAmount": 600,
            "minSpend": 3500,
            "daysToComplete": 90,
            "description": "10% cashback first 3 months up to $3,500 + $139 annual fee rebate first year"
        },
        "rewardRules": [
            {"id": 19, "category": "GROCERY", "rewardRate": 0.0300, "monthlyCapAmount": 1250.00, "description": "3% on groceries (up to $15,000/year)"},
            {"id": 20, "category": "GAS", "rewardRate": 0.0300, "monthlyCapAmount": 1250.00, "description": "3% on gas & EV charging (up to $15,000/year)"},
            {"id": 21, "category": "TRANSIT", "rewardRate": 0.0300, "monthlyCapAmount": 1250.00, "description": "3% on public transit (up to $15,000/year)"},
            {"id": 22, "category": "RECURRING", "rewardRate": 0.0300, "monthlyCapAmount": 1250.00, "description": "3% on recurring bills (up to $15,000/year)"},
            {"id": 23, "category": "STREAMING", "rewardRate": 0.0300, "monthlyCapAmount": 1250.00, "description": "3% on streaming & digital media (up to $15,000/year)"}
        ]
    },
    {
        "id": 31,
        "bank": "Rogers",
        "name": "World Elite Mastercard",
        "cardType": "MASTERCARD",
        "annualFee": 0.00,
        "baseRewardRate": 0.0150,
        "imageUrl": '{"gradient": "linear-gradient(135deg, #e31837 0%, #b8132c 100%)", "textColor": "white"}',
        "applyUrl": "https://www.rogersbank.com/en/rogers_worldelite_mastercard_details",
        "noFxFee": False,
        "signupBonus": {
            "bonusAmount": 25,
            "minSpend": 500,
            "daysToComplete": 90,
            "description": "$25 bonus + 3% on USD purchases"
        },
        "rewardRules": [
            {"id": 69, "category": "TRAVEL", "rewardRate": 0.0300, "monthlyCapAmount": None, "description": "3% on foreign currency purchases (No FX fee - effective 5.5% savings!)"},
            {"id": 104, "category": "FOREIGN", "rewardRate": 0.0300, "monthlyCapAmount": None, "description": "3% cashback + No FX fee (effective 5.5% savings vs cards with FX fees)"},
            {"id": 127, "category": "TELECOM", "rewardRate": 0.0300, "monthlyCapAmount": None, "description": "3% on Rogers/Fido/Shaw services"},
            {"id": 153, "category": "RETAIL", "rewardRate": 0.0150, "monthlyCapAmount": None, "description": "1.5% on retail shopping"}
        ]
    }
]


def main():
    """Import sample data to storage"""
    storage = CardStorage()

    print("Importing credit card data...")
    cards = storage.save_cards_from_api(SAMPLE_DATA)

    print(f"Successfully imported {len(cards)} credit cards!")
    print("\nImported cards:")
    for card in cards:
        print(f"  - {card.bank} {card.name} (ID: {card.id})")

    print(f"\nData saved to: {storage.cards_file}")


if __name__ == "__main__":
    main()
