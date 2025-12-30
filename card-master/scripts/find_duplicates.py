#!/usr/bin/env python3
"""Find and optionally delete duplicate cards."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import re
from collections import defaultdict
from src.services.database import Database


def find_duplicates(bank: str = None, delete: bool = False):
    db = Database()
    cards = db.get_all_cards()

    if bank:
        cards = [c for c in cards if c.bank == bank]

    print(f"Total cards: {len(cards)}")

    # Group by normalized name
    groups = defaultdict(list)
    for card in cards:
        # Normalize name more aggressively
        norm_name = re.sub(r'\s+', ' ', card.name.lower().strip())
        norm_name = norm_name.replace('mastercard', 'mc').replace('world elite', 'we')
        norm_name = norm_name.replace('visa', 'v').replace('infinite', 'inf')
        # Fix common typos and variations
        norm_name = norm_name.replace('viporter', 'vipoter').replace('vipilot', 'vipoter')
        norm_name = norm_name.replace('u.s.', 'us').replace('u.s', 'us')
        norm_name = re.sub(r'[^\w\s]', '', norm_name)  # Remove punctuation
        # Remove redundant bank name prefix if it appears
        bank_lower = card.bank.lower()
        if norm_name.startswith(bank_lower + ' '):
            norm_name_no_bank = norm_name[len(bank_lower)+1:]
            # Use the version without bank prefix as the key
            norm_name = norm_name_no_bank
        groups[(card.bank, norm_name)].append(card)

    print("\nDuplicate groups:")
    duplicates_to_delete = []

    for (bank_name, name), cards_list in groups.items():
        if len(cards_list) > 1:
            print(f"\n  [{bank_name}] {name}:")
            # Find the best one (with valid image and most complete data)
            best = None
            for c in cards_list:
                has_valid_img = c.image_url and any(c.image_url.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.webp'])
                has_rules = len(c.reward_rules) > 0 if c.reward_rules else False
                img_status = "IMG:OK" if has_valid_img else "IMG:NO"
                rules_status = f"RULES:{len(c.reward_rules) if c.reward_rules else 0}"
                print(f"    ID {c.id}: {c.name} [{img_status}] [{rules_status}]")
                if has_valid_img and has_rules and best is None:
                    best = c

            # If no card has valid image and rules, pick the one with most rules
            if best is None:
                best = max(cards_list, key=lambda c: len(c.reward_rules) if c.reward_rules else 0)

            print(f"    -> Keep ID {best.id}")
            # Mark others for deletion
            for c in cards_list:
                if c.id != best.id:
                    duplicates_to_delete.append(c.id)

    print(f"\n\nCards to delete: {duplicates_to_delete}")

    if delete and duplicates_to_delete:
        conn = db._get_connection()
        cursor = conn.cursor()
        try:
            for card_id in duplicates_to_delete:
                cursor.execute("DELETE FROM reward_rules WHERE card_id = ?", (card_id,))
                cursor.execute("DELETE FROM signup_bonuses WHERE card_id = ?", (card_id,))
                cursor.execute("DELETE FROM cards WHERE id = ?", (card_id,))
                print(f"  Deleted card ID {card_id}")
            conn.commit()
            print(f"\nDeleted {len(duplicates_to_delete)} duplicate cards")
        finally:
            conn.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--bank", "-b", help="Filter by bank")
    parser.add_argument("--delete", "-d", action="store_true", help="Actually delete duplicates")
    args = parser.parse_args()

    find_duplicates(bank=args.bank, delete=args.delete)
