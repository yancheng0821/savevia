"""
Card storage service - JSON file based storage for credit card data.
"""

import json
from decimal import Decimal
from pathlib import Path
from typing import Optional

from src.models import CreditCard


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Decimal types"""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class CardStorage:
    """JSON file storage for credit card data"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cards_file = self.data_dir / "cards.json"

    def save_cards(self, cards: list[CreditCard]) -> None:
        """Save cards to JSON file"""
        data = {
            "cards": [card.model_dump() for card in cards],
            "count": len(cards),
        }
        with open(self.cards_file, "w", encoding="utf-8") as f:
            json.dump(data, f, cls=DecimalEncoder, ensure_ascii=False, indent=2)

    def load_cards(self) -> list[CreditCard]:
        """Load cards from JSON file"""
        if not self.cards_file.exists():
            return []

        with open(self.cards_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        cards = []
        for card_data in data.get("cards", []):
            try:
                # Convert float back to Decimal for rate fields
                if "annual_fee" in card_data:
                    card_data["annual_fee"] = Decimal(str(card_data["annual_fee"]))
                if "base_reward_rate" in card_data:
                    card_data["base_reward_rate"] = Decimal(
                        str(card_data["base_reward_rate"])
                    )

                # Convert reward rules
                if "reward_rules" in card_data:
                    for rule in card_data["reward_rules"]:
                        if "reward_rate" in rule:
                            rule["reward_rate"] = Decimal(str(rule["reward_rate"]))
                        if rule.get("monthly_cap_amount"):
                            rule["monthly_cap_amount"] = Decimal(
                                str(rule["monthly_cap_amount"])
                            )

                cards.append(CreditCard(**card_data))
            except Exception as e:
                print(f"Error loading card: {e}")
                continue

        return cards

    def save_cards_from_api(self, api_data: list[dict]) -> list[CreditCard]:
        """Save cards from savevia.app API format"""
        cards = [CreditCard.from_api(card_data) for card_data in api_data]
        self.save_cards(cards)
        return cards

    def get_card_by_id(self, card_id: int) -> Optional[CreditCard]:
        """Get a card by its ID"""
        cards = self.load_cards()
        for card in cards:
            if card.id == card_id:
                return card
        return None

    def get_cards_by_bank(self, bank: str) -> list[CreditCard]:
        """Get all cards from a specific bank"""
        cards = self.load_cards()
        return [card for card in cards if card.bank.upper() == bank.upper()]
