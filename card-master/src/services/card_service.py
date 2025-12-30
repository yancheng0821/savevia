"""
Card service - Business logic for credit card queries and ranking.

Supports both JSON file storage and SQLite database.
"""

from decimal import Decimal
from typing import Optional

from src.models import CreditCard, CardRankItem, CATEGORY_CN_NAMES
from src.services.storage import CardStorage
from src.services.database import Database


class CardService:
    """Business logic service for credit card operations.

    Supports two storage backends:
    - SQLite database (preferred for scraped cards)
    - JSON file (legacy, for imported cards)

    When both have data, SQLite takes priority.
    """

    def __init__(self, storage: Optional[CardStorage] = None, database: Optional[Database] = None):
        self.storage = storage or CardStorage()
        self.database = database

    def _use_database(self) -> bool:
        """Check if database should be used (has data)"""
        if self.database:
            stats = self.database.get_stats()
            return stats.get("total_cards", 0) > 0
        return False

    def get_all_cards(self) -> list[CreditCard]:
        """Get all credit cards from storage"""
        # Try database first
        if self._use_database():
            return self.database.get_all_cards()
        # Fallback to JSON
        return self.storage.load_cards()

    def get_card_by_id(self, card_id: int) -> Optional[CreditCard]:
        """Get a card by ID"""
        if self._use_database():
            return self.database.get_card_by_id(card_id)
        return self.storage.get_card_by_id(card_id)

    def get_cards_by_bank(self, bank: str) -> list[CreditCard]:
        """Get all cards from a bank"""
        if self._use_database():
            return self.database.get_cards_by_bank(bank)
        return self.storage.get_cards_by_bank(bank)

    def get_all_banks(self) -> list[str]:
        """Get list of all unique banks"""
        cards = self.get_all_cards()
        banks = sorted(set(card.bank for card in cards))
        return banks

    def get_all_categories(self) -> list[dict]:
        """Get list of all spending categories with Chinese names"""
        cards = self.get_all_cards()

        # Collect all categories that have at least one card with a rule
        categories_with_cards = set()
        for card in cards:
            for rule in card.reward_rules:
                categories_with_cards.add(rule.category)

        # Return sorted list with Chinese names
        result = []
        for category in sorted(categories_with_cards):
            result.append({
                "code": category,
                "name": CATEGORY_CN_NAMES.get(category, category),
            })
        return result

    def rank_cards_by_category(
        self,
        category: str,
        limit: Optional[int] = None,
        include_base_rate: bool = True,
    ) -> list[CardRankItem]:
        """
        Rank cards by reward rate for a specific spending category.

        Args:
            category: Spending category code (e.g., 'DINING', 'GROCERY')
            limit: Maximum number of cards to return
            include_base_rate: Include cards that only have base rate for this category

        Returns:
            List of CardRankItem sorted by reward rate (descending)
        """
        cards = self.get_all_cards()
        rank_items = []

        for card in cards:
            rule = card.get_rule_for_category(category)

            if rule:
                # Card has specific rule for this category
                rank_items.append(
                    CardRankItem(
                        card=card,
                        category=category,
                        reward_rate=rule.reward_rate,
                        reward_rate_percent=rule.reward_rate_percent,
                        monthly_cap=rule.monthly_cap_amount,
                        description=rule.description,
                    )
                )
            elif include_base_rate and card.base_reward_rate > 0:
                # Use base reward rate
                rank_items.append(
                    CardRankItem(
                        card=card,
                        category=category,
                        reward_rate=card.base_reward_rate,
                        reward_rate_percent=card.base_reward_rate_percent,
                        monthly_cap=None,
                        description=f"Base rate: {card.base_reward_rate_percent}",
                    )
                )

        # Sort by reward rate descending
        rank_items.sort(key=lambda x: x.reward_rate, reverse=True)

        if limit:
            rank_items = rank_items[:limit]

        return rank_items

    def get_best_card_for_category(self, category: str) -> Optional[CardRankItem]:
        """Get the best card for a specific category"""
        ranked = self.rank_cards_by_category(category, limit=1)
        return ranked[0] if ranked else None

    def get_cards_with_no_annual_fee(self) -> list[CreditCard]:
        """Get all cards with no annual fee"""
        cards = self.get_all_cards()
        return [card for card in cards if card.annual_fee == 0]

    def get_cards_with_no_fx_fee(self) -> list[CreditCard]:
        """Get all cards with no foreign transaction fee"""
        cards = self.get_all_cards()
        return [card for card in cards if card.no_fx_fee]

    def search_cards(self, query: str) -> list[CreditCard]:
        """Search cards by name or bank"""
        cards = self.get_all_cards()
        query = query.lower()
        return [
            card
            for card in cards
            if query in card.name.lower() or query in card.bank.lower()
        ]

    def get_summary_stats(self) -> dict:
        """Get summary statistics"""
        cards = self.get_all_cards()

        if not cards:
            return {
                "total_cards": 0,
                "total_banks": 0,
                "no_annual_fee_cards": 0,
                "no_fx_fee_cards": 0,
                "avg_annual_fee": 0,
            }

        return {
            "total_cards": len(cards),
            "total_banks": len(set(card.bank for card in cards)),
            "no_annual_fee_cards": len([c for c in cards if c.annual_fee == 0]),
            "no_fx_fee_cards": len([c for c in cards if c.no_fx_fee]),
            "avg_annual_fee": float(
                sum(card.annual_fee for card in cards) / len(cards)
            ),
        }
