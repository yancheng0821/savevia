"""
SQLite database storage for credit card data.
"""

import sqlite3
import json
from pathlib import Path
from decimal import Decimal
from typing import Optional
from datetime import datetime

from src.models import CreditCard, SignupBonus, RewardRule


class Database:
    """SQLite database for storing credit card information."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "data" / "cards.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create cards table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bank TEXT NOT NULL,
                name TEXT NOT NULL,
                card_type TEXT DEFAULT 'VISA',
                annual_fee REAL DEFAULT 0,
                base_reward_rate REAL DEFAULT 0.01,
                image_url TEXT,
                apply_url TEXT,
                no_fx_fee INTEGER DEFAULT 0,
                source_url TEXT,
                raw_content TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(bank, name)
            )
        """)

        # Create signup_bonuses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signup_bonuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER NOT NULL,
                bonus_amount INTEGER DEFAULT 0,
                min_spend INTEGER DEFAULT 0,
                days_to_complete INTEGER DEFAULT 90,
                description TEXT,
                FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
            )
        """)

        # Create reward_rules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reward_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                reward_rate REAL NOT NULL,
                monthly_cap_amount REAL,
                annual_cap_amount REAL,
                description TEXT,
                FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
            )
        """)

        # Create bank_card_urls table for discovered card URLs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bank_card_urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bank TEXT NOT NULL,
                card_name TEXT,
                url TEXT NOT NULL,
                scraped INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(url)
            )
        """)

        # Create banks table for bank configurations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS banks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                cards_url TEXT NOT NULL,
                logo_url TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

        # Initialize default banks if table is empty
        self._init_default_banks()

    def _init_default_banks(self):
        """Initialize default bank configurations."""
        default_banks = [
            ("BMO", "https://www.bmo.com/main/personal/credit-cards/", None),
            ("TD", "https://www.td.com/ca/en/personal-banking/products/credit-cards", None),
            ("RBC", "https://www.rbcroyalbank.com/credit-cards/", None),
            ("CIBC", "https://www.cibc.com/en/personal-banking/credit-cards.html", None),
            ("Scotiabank", "https://www.scotiabank.com/ca/en/personal/credit-cards.html", None),
            ("AMEX", "https://www.americanexpress.com/en-ca/credit-cards/", None),
            ("Tangerine", "https://www.tangerine.ca/en/products/spending/creditcard", None),
            ("Simplii", "https://www.simplii.com/en/credit-cards.html", None),
            ("Rogers", "https://www.rogersbank.com/en/credit_cards", None),
            ("Desjardins", "https://www.desjardins.com/ca/personal/loans-credit/credit-cards/index.jsp", None),
            ("HSBC", "https://www.hsbc.ca/credit-cards/", None),
            ("National Bank", "https://www.nbc.ca/personal/credit-cards.html", None),
        ]

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Check if banks table is empty
            cursor.execute("SELECT COUNT(*) as count FROM banks")
            if cursor.fetchone()["count"] == 0:
                cursor.executemany("""
                    INSERT OR IGNORE INTO banks (name, cards_url, logo_url)
                    VALUES (?, ?, ?)
                """, default_banks)
                conn.commit()
        finally:
            conn.close()

    def save_card(self, card: CreditCard, source_url: str = None, raw_content: str = None) -> int:
        """
        Save or update a credit card.
        Returns the card ID.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Insert or update card
            cursor.execute("""
                INSERT INTO cards (bank, name, card_type, annual_fee, base_reward_rate,
                                   image_url, apply_url, no_fx_fee, source_url, raw_content, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(bank, name) DO UPDATE SET
                    card_type = excluded.card_type,
                    annual_fee = excluded.annual_fee,
                    base_reward_rate = excluded.base_reward_rate,
                    image_url = excluded.image_url,
                    apply_url = excluded.apply_url,
                    no_fx_fee = excluded.no_fx_fee,
                    source_url = excluded.source_url,
                    raw_content = excluded.raw_content,
                    updated_at = excluded.updated_at
            """, (
                card.bank,
                card.name,
                card.card_type,
                float(card.annual_fee),
                float(card.base_reward_rate),
                card.image_url,
                card.apply_url,
                1 if card.no_fx_fee else 0,
                source_url,
                raw_content,
                datetime.now().isoformat()
            ))

            # Get card ID
            cursor.execute("SELECT id FROM cards WHERE bank = ? AND name = ?", (card.bank, card.name))
            card_id = cursor.fetchone()["id"]

            # Delete existing signup bonus and reward rules
            cursor.execute("DELETE FROM signup_bonuses WHERE card_id = ?", (card_id,))
            cursor.execute("DELETE FROM reward_rules WHERE card_id = ?", (card_id,))

            # Insert signup bonus
            if card.signup_bonus:
                cursor.execute("""
                    INSERT INTO signup_bonuses (card_id, bonus_amount, min_spend, days_to_complete, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    card_id,
                    card.signup_bonus.bonus_amount,
                    card.signup_bonus.min_spend,
                    card.signup_bonus.days_to_complete,
                    card.signup_bonus.description
                ))

            # Insert reward rules
            for rule in card.reward_rules:
                cursor.execute("""
                    INSERT INTO reward_rules (card_id, category, reward_rate, monthly_cap_amount, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    card_id,
                    rule.category,
                    float(rule.reward_rate),
                    float(rule.monthly_cap_amount) if rule.monthly_cap_amount else None,
                    rule.description
                ))

            conn.commit()
            return card_id

        finally:
            conn.close()

    def get_all_cards(self) -> list[CreditCard]:
        """Get all credit cards from database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cards ORDER BY bank, name")
            rows = cursor.fetchall()

            cards = []
            for row in rows:
                card = self._row_to_card(cursor, row)
                cards.append(card)

            return cards
        finally:
            conn.close()

    def get_card_by_id(self, card_id: int) -> Optional[CreditCard]:
        """Get a card by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cards WHERE id = ?", (card_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_card(cursor, row)
            return None
        finally:
            conn.close()

    def get_cards_by_bank(self, bank: str) -> list[CreditCard]:
        """Get all cards from a specific bank."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM cards WHERE bank LIKE ? ORDER BY name", (f"%{bank}%",))
            rows = cursor.fetchall()

            cards = []
            for row in rows:
                card = self._row_to_card(cursor, row)
                cards.append(card)

            return cards
        finally:
            conn.close()

    def _row_to_card(self, cursor: sqlite3.Cursor, row: sqlite3.Row) -> CreditCard:
        """Convert database row to CreditCard model."""
        card_id = row["id"]

        # Get signup bonus
        cursor.execute("SELECT * FROM signup_bonuses WHERE card_id = ?", (card_id,))
        bonus_row = cursor.fetchone()
        signup_bonus = None
        if bonus_row:
            signup_bonus = SignupBonus(
                bonus_amount=bonus_row["bonus_amount"],
                min_spend=bonus_row["min_spend"],
                days_to_complete=bonus_row["days_to_complete"],
                description=bonus_row["description"]
            )

        # Get reward rules
        cursor.execute("SELECT * FROM reward_rules WHERE card_id = ?", (card_id,))
        rule_rows = cursor.fetchall()
        reward_rules = [
            RewardRule(
                category=r["category"],
                reward_rate=Decimal(str(r["reward_rate"])),
                monthly_cap_amount=Decimal(str(r["monthly_cap_amount"])) if r["monthly_cap_amount"] else None,
                description=r["description"]
            )
            for r in rule_rows
        ]

        return CreditCard(
            id=card_id,
            bank=row["bank"],
            name=row["name"],
            card_type=row["card_type"],
            annual_fee=Decimal(str(row["annual_fee"])),
            base_reward_rate=Decimal(str(row["base_reward_rate"])),
            image_url=row["image_url"],
            apply_url=row["apply_url"],
            no_fx_fee=bool(row["no_fx_fee"]),
            signup_bonus=signup_bonus,
            reward_rules=reward_rules
        )

    def save_bank_card_url(self, bank: str, url: str, card_name: str = None):
        """Save a discovered card URL for later scraping."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR IGNORE INTO bank_card_urls (bank, card_name, url)
                VALUES (?, ?, ?)
            """, (bank, card_name, url))
            conn.commit()
        finally:
            conn.close()

    def get_unscraped_urls(self, bank: str = None) -> list[dict]:
        """Get URLs that haven't been scraped yet."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if bank:
                cursor.execute("""
                    SELECT * FROM bank_card_urls
                    WHERE scraped = 0 AND bank LIKE ?
                """, (f"%{bank}%",))
            else:
                cursor.execute("SELECT * FROM bank_card_urls WHERE scraped = 0")

            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def mark_url_scraped(self, url: str):
        """Mark a URL as scraped."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE bank_card_urls SET scraped = 1 WHERE url = ?", (url,))
            conn.commit()
        finally:
            conn.close()

    def get_stats(self) -> dict:
        """Get database statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) as count FROM cards")
            total_cards = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(DISTINCT bank) as count FROM cards")
            total_banks = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) as count FROM cards WHERE annual_fee = 0")
            no_fee_cards = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) as count FROM cards WHERE no_fx_fee = 1")
            no_fx_cards = cursor.fetchone()["count"]

            return {
                "total_cards": total_cards,
                "total_banks": total_banks,
                "no_annual_fee_cards": no_fee_cards,
                "no_fx_fee_cards": no_fx_cards
            }
        finally:
            conn.close()

    # ==================== Bank CRUD Methods ====================

    def get_all_banks(self, active_only: bool = True) -> list[dict]:
        """Get all banks from database."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            if active_only:
                cursor.execute("SELECT * FROM banks WHERE is_active = 1 ORDER BY name")
            else:
                cursor.execute("SELECT * FROM banks ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_bank_by_name(self, name: str) -> Optional[dict]:
        """Get bank by name."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM banks WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_bank_by_id(self, bank_id: int) -> Optional[dict]:
        """Get bank by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM banks WHERE id = ?", (bank_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def add_bank(self, name: str, cards_url: str, logo_url: str = None) -> int:
        """Add a new bank. Returns the bank ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO banks (name, cards_url, logo_url)
                VALUES (?, ?, ?)
            """, (name, cards_url, logo_url))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def update_bank(self, bank_id: int, name: str = None, cards_url: str = None,
                    logo_url: str = None, is_active: bool = None) -> bool:
        """Update bank information. Returns True if updated."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Build dynamic update query
            updates = []
            values = []

            if name is not None:
                updates.append("name = ?")
                values.append(name)
            if cards_url is not None:
                updates.append("cards_url = ?")
                values.append(cards_url)
            if logo_url is not None:
                updates.append("logo_url = ?")
                values.append(logo_url)
            if is_active is not None:
                updates.append("is_active = ?")
                values.append(1 if is_active else 0)

            if not updates:
                return False

            updates.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(bank_id)

            query = f"UPDATE banks SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def delete_bank(self, bank_id: int) -> bool:
        """Delete a bank. Returns True if deleted."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM banks WHERE id = ?", (bank_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_bank_card_listings(self) -> dict[str, str]:
        """Get bank card listings as a dictionary (for Agent compatibility)."""
        banks = self.get_all_banks(active_only=True)
        return {bank["name"]: bank["cards_url"] for bank in banks}
