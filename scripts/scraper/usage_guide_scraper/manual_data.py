#!/usr/bin/env python3
"""
Manual data entry for usage guide tips.
This module allows manually entering card usage tips from web research,
then translating and generating SQL.

Usage:
    python -m usage_guide_scraper.manual_data --input tips_data.json --output tips_update.sql
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

from .models import UsageTip, TranslatedTip, CardRewardInfo, TipType, RewardType, TransferPartner
from .translator import Translator, MockTranslator
from .sql_generator import SQLGenerator
from .config import OUTPUT_DIR, OPENAI_API_KEY


# Sample data structure for reference
SAMPLE_DATA = {
    "cards": [
        {
            "card_id": 1,
            "card_name": "Cobalt Card",
            "bank": "AMEX",
            "reward_info": {
                "reward_type": "POINTS",
                "point_value": 0.02,
                "point_program": "Membership Rewards",
                "transfer_partners": [
                    {"partner": "Aeroplan", "ratio": "1:1", "type": "AIRLINE"},
                    {"partner": "Hilton Honors", "ratio": "1:2", "type": "HOTEL"},
                    {"partner": "Marriott Bonvoy", "ratio": "1:1.2", "type": "HOTEL"}
                ]
            },
            "tips": [
                {
                    "tip_type": "BEST_USE",
                    "title": "Dining and Food Delivery",
                    "content": "Earn 5x points at restaurants, bars, and food delivery services including Uber Eats and DoorDash. This is one of the highest dining reward rates in Canada.",
                    "icon": "dining",
                    "priority": 1
                },
                {
                    "tip_type": "BEST_USE",
                    "title": "Grocery Shopping",
                    "content": "Earn 5x points at grocery stores. Ideal for everyday shopping at major chains like Loblaws, Sobeys, and Metro.",
                    "icon": "grocery",
                    "priority": 2
                },
                {
                    "tip_type": "REDEMPTION",
                    "title": "Transfer to Aeroplan for Best Value",
                    "content": "Transfer points 1:1 to Aeroplan for flights worth up to 2+ cents per point. Book reward flights on Air Canada and Star Alliance partners.",
                    "icon": "transfer",
                    "priority": 1
                },
                {
                    "tip_type": "STACKING",
                    "title": "Combine with Amex Offers",
                    "content": "Stack your earnings by adding Amex Offers in the app for additional discounts at participating merchants.",
                    "icon": "stack",
                    "priority": 1
                },
                {
                    "tip_type": "AVOID",
                    "title": "Foreign Transactions",
                    "content": "Avoid using this card abroad as it charges 2.5% foreign transaction fee. Use a no-FX fee card instead.",
                    "icon": "warning",
                    "priority": 1
                }
            ]
        }
    ]
}


def load_tips_from_json(filepath: str) -> Dict[str, Any]:
    """Load tips data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def convert_to_usage_tips(data: Dict[str, Any]) -> tuple:
    """Convert JSON data to UsageTip and CardRewardInfo objects"""
    all_tips = []
    reward_infos = []

    for card_data in data.get("cards", []):
        card_id = card_data["card_id"]

        # Convert tips
        for tip_data in card_data.get("tips", []):
            tip = UsageTip(
                card_id=card_id,
                tip_type=TipType(tip_data["tip_type"]),
                title_en=tip_data["title"],
                content_en=tip_data["content"],
                icon=tip_data.get("icon"),
                priority=tip_data.get("priority", 0)
            )
            all_tips.append(tip)

        # Convert reward info
        if "reward_info" in card_data:
            ri = card_data["reward_info"]
            transfer_partners = []
            for tp in ri.get("transfer_partners", []):
                transfer_partners.append(TransferPartner(
                    partner_name=tp["partner"],
                    ratio=tp["ratio"],
                    program_type=tp["type"]
                ))

            reward_info = CardRewardInfo(
                card_id=card_id,
                reward_type=RewardType(ri.get("reward_type", "CASHBACK")),
                point_value=ri.get("point_value"),
                point_program=ri.get("point_program"),
                transfer_partners=transfer_partners
            )
            reward_infos.append(reward_info)

    return all_tips, reward_infos


def generate_sample_json(output_path: str):
    """Generate a sample JSON file for reference"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(SAMPLE_DATA, f, indent=2, ensure_ascii=False)
    print(f"Sample JSON saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert manual card tips data to SQL with translation'
    )
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Input JSON file with tips data'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output SQL filename'
    )
    parser.add_argument(
        '--generate-sample',
        action='store_true',
        help='Generate a sample JSON file'
    )
    parser.add_argument(
        '--no-translate',
        action='store_true',
        help='Skip translation (English only)'
    )
    parser.add_argument(
        '--mock-translate',
        action='store_true',
        help='Use mock translator for testing'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview without generating SQL'
    )

    args = parser.parse_args()

    if args.generate_sample:
        sample_path = OUTPUT_DIR / "sample_tips_data.json"
        generate_sample_json(str(sample_path))
        return

    if not args.input:
        print("Error: --input required. Use --generate-sample to create a template.")
        return

    print("=" * 60)
    print("Manual Data to SQL Converter")
    print("=" * 60)

    # Load data
    print(f"Loading data from: {args.input}")
    data = load_tips_from_json(args.input)

    # Convert to objects
    tips, reward_infos = convert_to_usage_tips(data)
    print(f"Loaded {len(tips)} tips for {len(data.get('cards', []))} cards")

    if args.dry_run:
        print("\n[DRY RUN] Would process:")
        for tip in tips:
            print(f"  [{tip.tip_type.value}] Card {tip.card_id}: {tip.title_en[:40]}...")
        return

    # Translate
    translated_tips = []
    if args.no_translate:
        print("\n[SKIPPING TRANSLATION]")
        for tip in tips:
            translated_tips.append(TranslatedTip(
                card_id=tip.card_id,
                tip_type=tip.tip_type,
                title_json={"en": tip.title_en},
                content_json={"en": tip.content_en},
                icon=tip.icon,
                priority=tip.priority
            ))
    else:
        print("\nTranslating tips...")
        if args.mock_translate:
            translator = MockTranslator()
        else:
            if not OPENAI_API_KEY:
                print("Error: OPENAI_API_KEY not set")
                return
            translator = Translator()
        translated_tips = translator.batch_translate(tips)

    # Generate SQL
    print("\nGenerating SQL...")
    generator = SQLGenerator()
    sql = generator.generate_sql(translated_tips, reward_infos, args.output)

    print("\nDone!")


if __name__ == "__main__":
    main()
