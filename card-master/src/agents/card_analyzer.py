"""
Card Analyzer - Extracts credit card information from scraped page content.

This module provides a structured prompt template for LLM (Claude) to analyze
credit card detail pages and extract reward information.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
import json
import re

from src.models import CreditCard, SignupBonus, RewardRule, SpendingCategory


# Spending categories mapping for LLM reference
CATEGORY_MAPPING = {
    "dining": "DINING",
    "restaurant": "DINING",
    "餐饮": "DINING",
    "餐厅": "DINING",
    "grocery": "GROCERY",
    "groceries": "GROCERY",
    "supermarket": "GROCERY",
    "超市": "GROCERY",
    "gas": "GAS",
    "fuel": "GAS",
    "加油": "GAS",
    "travel": "TRAVEL",
    "hotel": "TRAVEL",
    "flight": "TRAVEL",
    "air canada": "TRAVEL",
    "旅行": "TRAVEL",
    "transit": "TRANSIT",
    "uber": "TRANSIT",
    "lyft": "TRANSIT",
    "public transit": "TRANSIT",
    "公交": "TRANSIT",
    "streaming": "STREAMING",
    "netflix": "STREAMING",
    "spotify": "STREAMING",
    "流媒体": "STREAMING",
    "entertainment": "ENTERTAINMENT",
    "娱乐": "ENTERTAINMENT",
    "personal services": "PERSONAL_SERVICES",
    "beauty": "PERSONAL_SERVICES",
    "spa": "PERSONAL_SERVICES",
    "retail": "RETAIL",
    "shopping": "RETAIL",
    "购物": "RETAIL",
    "home improvement": "HOME_IMPROVEMENT",
    "hardware": "HOME_IMPROVEMENT",
    "recurring": "RECURRING",
    "bills": "RECURRING",
    "subscription": "RECURRING",
    "pharmacy": "PHARMACY",
    "drug store": "PHARMACY",
    "药店": "PHARMACY",
    "foreign": "FOREIGN",
    "international": "FOREIGN",
    "境外": "FOREIGN",
    "online": "ONLINE_SHOPPING",
    "ev charging": "EV_CHARGING",
    "electric vehicle": "EV_CHARGING",
    "telecom": "TELECOM",
    "rogers": "TELECOM",
    "fido": "TELECOM",
    "bell": "TELECOM",
    "通讯": "TELECOM",
}


@dataclass
class AnalysisPrompt:
    """Prompt template for LLM analysis"""
    page_content: str
    bank: str
    url: str

    def generate_prompt(self) -> str:
        """Generate the analysis prompt for Claude"""
        return f"""Analyze this credit card page and extract the reward information.

## Page Source
Bank: {self.bank}
URL: {self.url}

## Page Content:
{self.page_content[:15000]}

## Instructions:
Extract the following information in JSON format:

```json
{{
    "name": "Card name (without bank name prefix)",
    "card_type": "VISA | MASTERCARD | AMEX",
    "annual_fee": 0.00,
    "base_reward_rate": 0.01,
    "no_fx_fee": false,
    "apply_url": "URL to apply for the card",
    "signup_bonus": {{
        "bonus_amount": 0,
        "min_spend": 0,
        "days_to_complete": 90,
        "description": "Description of the bonus"
    }},
    "reward_rules": [
        {{
            "category": "DINING | GROCERY | GAS | TRAVEL | TRANSIT | STREAMING | ENTERTAINMENT | PERSONAL_SERVICES | RETAIL | HOME_IMPROVEMENT | RECURRING | PHARMACY | FOREIGN | ONLINE_SHOPPING | EV_CHARGING | TELECOM",
            "reward_rate": 0.05,
            "monthly_cap_amount": null,
            "description": "5% on dining"
        }}
    ]
}}
```

## Category Reference:
- DINING: Restaurants, food delivery
- GROCERY: Supermarkets, grocery stores
- GAS: Gas stations, fuel
- TRAVEL: Hotels, flights, travel agencies, Air Canada
- TRANSIT: Uber, Lyft, public transit, rideshare
- STREAMING: Netflix, Spotify, streaming services
- ENTERTAINMENT: Movies, concerts, events
- PERSONAL_SERVICES: Spa, beauty, hair salon
- RETAIL: General shopping, department stores
- HOME_IMPROVEMENT: Hardware stores, home renovation
- RECURRING: Bills, subscriptions, recurring payments
- PHARMACY: Drug stores, pharmacies
- FOREIGN: International/foreign currency purchases
- ONLINE_SHOPPING: Online retail purchases
- EV_CHARGING: Electric vehicle charging
- TELECOM: Rogers, Bell, Fido, Shaw, telecom services

## Important Notes:
1. Reward rates should be expressed as decimals (5% = 0.05)
2. Base reward rate is the rate for categories not listed
3. If no FX fee info found, assume no_fx_fee = false
4. Extract signup bonus if available
5. monthly_cap_amount is the monthly spending cap for bonus rate (null if unlimited)

Return ONLY the JSON, no other text.
"""


@dataclass
class AnalyzedCard:
    """Result of card analysis"""
    name: str
    bank: str
    card_type: str
    annual_fee: Decimal
    base_reward_rate: Decimal
    no_fx_fee: bool
    apply_url: Optional[str]
    signup_bonus: Optional[SignupBonus]
    reward_rules: list[RewardRule]
    source_url: str
    raw_content: str

    def to_credit_card(self, card_id: int) -> CreditCard:
        """Convert to CreditCard model"""
        return CreditCard(
            id=card_id,
            bank=self.bank,
            name=self.name,
            card_type=self.card_type,
            annual_fee=self.annual_fee,
            base_reward_rate=self.base_reward_rate,
            no_fx_fee=self.no_fx_fee,
            apply_url=self.apply_url,
            signup_bonus=self.signup_bonus,
            reward_rules=self.reward_rules,
        )


def parse_llm_response(response_text: str, bank: str, source_url: str, raw_content: str) -> AnalyzedCard:
    """
    Parse the LLM response JSON into AnalyzedCard.

    Args:
        response_text: JSON response from LLM
        bank: Bank name
        source_url: Original page URL
        raw_content: Raw page content
    """
    # Extract JSON from response (handle markdown code blocks)
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = response_text.strip()

    data = json.loads(json_str)

    # Parse signup bonus
    signup_bonus = None
    if data.get("signup_bonus"):
        sb = data["signup_bonus"]
        if sb.get("bonus_amount", 0) > 0:
            signup_bonus = SignupBonus(
                bonus_amount=sb.get("bonus_amount", 0),
                min_spend=sb.get("min_spend", 0),
                days_to_complete=sb.get("days_to_complete", 90),
                description=sb.get("description"),
            )

    # Parse reward rules
    reward_rules = []
    for rule in data.get("reward_rules", []):
        category = rule.get("category", "OTHER").upper()
        # Validate category
        if category not in [c.value for c in SpendingCategory]:
            category = "OTHER"

        reward_rules.append(RewardRule(
            category=category,
            reward_rate=Decimal(str(rule.get("reward_rate", 0.01))),
            monthly_cap_amount=Decimal(str(rule["monthly_cap_amount"])) if rule.get("monthly_cap_amount") else None,
            description=rule.get("description"),
        ))

    return AnalyzedCard(
        name=data.get("name", "Unknown Card"),
        bank=bank,
        card_type=data.get("card_type", "VISA").upper(),
        annual_fee=Decimal(str(data.get("annual_fee", 0))),
        base_reward_rate=Decimal(str(data.get("base_reward_rate", 0.01))),
        no_fx_fee=data.get("no_fx_fee", False),
        apply_url=data.get("apply_url") or source_url,
        signup_bonus=signup_bonus,
        reward_rules=reward_rules,
        source_url=source_url,
        raw_content=raw_content,
    )


def create_analysis_prompt(page_content: str, bank: str, url: str) -> str:
    """Create the analysis prompt for Claude"""
    prompt = AnalysisPrompt(
        page_content=page_content,
        bank=bank,
        url=url,
    )
    return prompt.generate_prompt()
