#!/usr/bin/env python3
"""
Save Credit Card to Database - Saves analyzed credit card data to SQLite.

Usage:
    python scripts/save_card.py           # Interactive mode
    python scripts/save_card.py <json>    # Direct JSON input

The JSON should be the output from Claude's analysis of a credit card page.
"""

import sys
import json
from pathlib import Path
from decimal import Decimal

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.card_analyzer import parse_llm_response
from src.services.database import Database


def save_card_from_json(json_str: str, bank: str, source_url: str, raw_content: str = ""):
    """Save a card from JSON analysis result"""
    db = Database()

    # Parse the LLM response
    analyzed = parse_llm_response(
        response_text=json_str,
        bank=bank,
        source_url=source_url,
        raw_content=raw_content,
    )

    # Get next card ID
    stats = db.get_stats()
    next_id = stats.get("total_cards", 0) + 1

    # Convert to CreditCard
    card = analyzed.to_credit_card(card_id=next_id)

    # Save to database
    card_id = db.save_card(card, source_url=source_url, raw_content=raw_content)

    print(f"\n✅ Card saved successfully!")
    print(f"   ID: {card_id}")
    print(f"   Bank: {card.bank}")
    print(f"   Name: {card.name}")
    print(f"   Card Type: {card.card_type}")
    print(f"   Annual Fee: ${card.annual_fee}")
    print(f"   Base Rate: {card.base_reward_rate_percent}")
    print(f"   No FX Fee: {card.no_fx_fee}")

    if card.signup_bonus:
        print(f"\n🎁 Signup Bonus:")
        print(f"   Amount: {card.signup_bonus.bonus_amount}")
        print(f"   Min Spend: ${card.signup_bonus.min_spend}")
        print(f"   Days: {card.signup_bonus.days_to_complete}")

    if card.reward_rules:
        print(f"\n💰 Reward Rules ({len(card.reward_rules)}):")
        for rule in card.reward_rules:
            cap = f" (cap: ${rule.monthly_cap_amount}/mo)" if rule.monthly_cap_amount else ""
            print(f"   - {rule.category}: {rule.reward_rate_percent}{cap}")

    # Mark URL as scraped
    db.mark_url_scraped(source_url)

    return card_id


def interactive_mode():
    """Interactive mode for saving cards"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║     Save Credit Card - 保存信用卡分析结果到数据库                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    bank = input("Enter bank name (e.g., BMO, TD, AMEX): ").strip()
    if not bank:
        print("Error: Bank name is required")
        sys.exit(1)

    source_url = input("Enter source URL: ").strip()
    if not source_url:
        print("Error: Source URL is required")
        sys.exit(1)

    print("\nPaste the JSON analysis from Claude (press Enter twice when done):")
    lines = []
    while True:
        try:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        except EOFError:
            break

    json_str = "\n".join(lines)

    if not json_str.strip():
        print("Error: No JSON provided")
        sys.exit(1)

    try:
        save_card_from_json(json_str, bank, source_url)
    except json.JSONDecodeError as e:
        print(f"\n❌ Error: Invalid JSON - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) == 1:
        interactive_mode()
    elif len(sys.argv) == 4:
        # Direct mode: json, bank, url
        json_str = sys.argv[1]
        bank = sys.argv[2]
        source_url = sys.argv[3]
        save_card_from_json(json_str, bank, source_url)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
