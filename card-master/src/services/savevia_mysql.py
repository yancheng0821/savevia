"""
MySQL connector for Savevia database.
Connects to the savevia MySQL database to fetch credit card data.
"""

import os
import json
from decimal import Decimal
from typing import Optional
from dataclasses import dataclass

try:
    import pymysql
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False


@dataclass
class SaveviaCard:
    """Credit card data from savevia.credit_cards table."""
    id: int
    bank: str
    name: str
    card_type: str
    annual_fee: Decimal
    base_reward_rate: Decimal
    signup_bonus_json: Optional[dict]
    image_url: Optional[str]
    apply_url: Optional[str]
    no_fx_fee: bool
    reward_type: str
    point_value: Optional[Decimal]
    point_program: Optional[str]
    reward_rules: list[dict]  # From reward_rules table


@dataclass
class SaveviaRewardRule:
    """Reward rule from savevia.reward_rules table."""
    id: int
    card_id: int
    category: str
    reward_rate: Decimal
    monthly_cap_amount: Optional[Decimal]
    mcc_codes: Optional[str]
    description: Optional[str]


class SaveviaMySQLDatabase:
    """
    MySQL database connector for Savevia.
    Reads credit card data from savevia.credit_cards and savevia.reward_rules.
    """

    def __init__(
        self,
        host: str = None,
        port: int = None,
        user: str = None,
        password: str = None,
        database: str = None,
    ):
        if not PYMYSQL_AVAILABLE:
            raise ImportError("pymysql is required. Install with: pip install pymysql")

        self.host = host or os.environ.get("MYSQL_HOST", "127.0.0.1")
        self.port = port or int(os.environ.get("MYSQL_PORT", "3306"))
        self.user = user or os.environ.get("MYSQL_USER", "savevia")
        self.password = password or os.environ.get("MYSQL_PASSWORD", "savevia123")
        self.database = database or os.environ.get("MYSQL_DATABASE", "savevia")

    def _get_connection(self):
        """Create a new database connection."""
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

    def get_all_cards(self, active_only: bool = True) -> list[SaveviaCard]:
        """
        Get all credit cards from savevia database.

        Args:
            active_only: Only return active cards (is_active = 1)

        Returns:
            List of SaveviaCard objects
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                # Get all cards
                sql = """
                    SELECT id, bank, name, card_type, annual_fee, base_reward_rate,
                           signup_bonus_json, image_url, apply_url, no_fx_fee,
                           reward_type, point_value, point_program
                    FROM credit_cards
                """
                if active_only:
                    sql += " WHERE is_active = 1"
                sql += " ORDER BY bank, name"

                cursor.execute(sql)
                rows = cursor.fetchall()

                cards = []
                for row in rows:
                    # Get reward rules for this card
                    cursor.execute("""
                        SELECT id, card_id, category, reward_rate, monthly_cap_amount,
                               mcc_codes, description
                        FROM reward_rules
                        WHERE card_id = %s
                    """, (row["id"],))
                    rules = cursor.fetchall()

                    # Parse signup_bonus_json
                    signup_bonus = None
                    if row["signup_bonus_json"]:
                        if isinstance(row["signup_bonus_json"], str):
                            signup_bonus = json.loads(row["signup_bonus_json"])
                        else:
                            signup_bonus = row["signup_bonus_json"]

                    card = SaveviaCard(
                        id=row["id"],
                        bank=row["bank"],
                        name=row["name"],
                        card_type=row["card_type"],
                        annual_fee=Decimal(str(row["annual_fee"])) if row["annual_fee"] else Decimal("0"),
                        base_reward_rate=Decimal(str(row["base_reward_rate"])) if row["base_reward_rate"] else Decimal("0.01"),
                        signup_bonus_json=signup_bonus,
                        image_url=row["image_url"],
                        apply_url=row["apply_url"],
                        no_fx_fee=bool(row["no_fx_fee"]),
                        reward_type=row["reward_type"] or "CASHBACK",
                        point_value=Decimal(str(row["point_value"])) if row["point_value"] else None,
                        point_program=row["point_program"],
                        reward_rules=[
                            {
                                "id": r["id"],
                                "category": r["category"],
                                "reward_rate": float(r["reward_rate"]),
                                "monthly_cap_amount": float(r["monthly_cap_amount"]) if r["monthly_cap_amount"] else None,
                                "mcc_codes": r["mcc_codes"],
                                "description": r["description"],
                            }
                            for r in rules
                        ],
                    )
                    cards.append(card)

                return cards
        finally:
            conn.close()

    def get_card_by_id(self, card_id: int) -> Optional[SaveviaCard]:
        """Get a single card by ID."""
        cards = self.get_all_cards(active_only=False)
        for card in cards:
            if card.id == card_id:
                return card
        return None

    def get_cards_by_bank(self, bank: str) -> list[SaveviaCard]:
        """Get all cards from a specific bank."""
        cards = self.get_all_cards()
        return [c for c in cards if c.bank.lower() == bank.lower()]

    def get_card_usage_tips(self, card_id: int) -> list[dict]:
        """Get usage tips for a card."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, tip_type, title_json, content_json, icon, priority
                    FROM card_usage_tips
                    WHERE card_id = %s AND is_active = 1
                    ORDER BY priority DESC
                """, (card_id,))
                rows = cursor.fetchall()

                tips = []
                for row in rows:
                    title = row["title_json"]
                    content = row["content_json"]
                    if isinstance(title, str):
                        title = json.loads(title)
                    if isinstance(content, str):
                        content = json.loads(content)

                    tips.append({
                        "id": row["id"],
                        "tip_type": row["tip_type"],
                        "title": title,
                        "content": content,
                        "icon": row["icon"],
                        "priority": row["priority"],
                    })
                return tips
        finally:
            conn.close()

    def get_stats(self) -> dict:
        """Get database statistics."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM credit_cards WHERE is_active = 1")
                total_cards = cursor.fetchone()["count"]

                cursor.execute("SELECT COUNT(DISTINCT bank) as count FROM credit_cards WHERE is_active = 1")
                total_banks = cursor.fetchone()["count"]

                cursor.execute("SELECT COUNT(*) as count FROM credit_cards WHERE is_active = 1 AND annual_fee = 0")
                no_fee_cards = cursor.fetchone()["count"]

                cursor.execute("SELECT COUNT(*) as count FROM credit_cards WHERE is_active = 1 AND no_fx_fee = 1")
                no_fx_cards = cursor.fetchone()["count"]

                return {
                    "total_cards": total_cards,
                    "total_banks": total_banks,
                    "no_annual_fee_cards": no_fee_cards,
                    "no_fx_fee_cards": no_fx_cards,
                }
        finally:
            conn.close()


# Test connection
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    db = SaveviaMySQLDatabase()
    stats = db.get_stats()
    print(f"Database stats: {stats}")

    cards = db.get_all_cards()
    print(f"\nTotal cards: {len(cards)}")
    for card in cards[:5]:
        print(f"  - {card.bank} {card.name}: {card.apply_url}")
