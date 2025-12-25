"""
SQL generator for card usage tips
"""

import json
from datetime import datetime
from typing import List, Optional, Set, Tuple
from pathlib import Path

from .models import TranslatedTip, ScrapedCardData, CardRewardInfo, TipType
from .config import OUTPUT_DIR


class SQLGenerator:
    """Generate SQL statements for card usage tips"""

    def __init__(self, output_dir: Path = OUTPUT_DIR):
        self.output_dir = output_dir
        self.generated_keys: Set[Tuple[int, str, str]] = set()

    def generate_sql(self, tips: List[TranslatedTip],
                     reward_infos: List[CardRewardInfo] = None,
                     output_filename: str = None) -> str:
        """Generate complete SQL file for usage tips"""
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"usage_tips_{timestamp}.sql"

        lines = []
        lines.append("-- Card Usage Tips Update")
        lines.append(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"-- Total tips: {len(tips)}")
        lines.append("")
        lines.append("START TRANSACTION;")
        lines.append("")

        # Generate INSERT statements for tips
        if tips:
            lines.append("-- ============================================")
            lines.append("-- USAGE TIPS")
            lines.append("-- ============================================")
            lines.append("")

            for tip in tips:
                sql = self._generate_tip_insert(tip)
                if sql:
                    lines.append(sql)
                    lines.append("")

        # Generate UPDATE statements for reward info
        if reward_infos:
            lines.append("-- ============================================")
            lines.append("-- CARD REWARD INFO UPDATES")
            lines.append("-- ============================================")
            lines.append("")

            for info in reward_infos:
                sql = self._generate_reward_info_update(info)
                if sql:
                    lines.append(sql)
                    lines.append("")

        lines.append("COMMIT;")
        lines.append("")
        lines.append("-- End of update")

        sql_content = "\n".join(lines)

        # Save to file
        output_path = self.output_dir / output_filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(sql_content)

        print(f"SQL saved to: {output_path}")
        return sql_content

    def _generate_tip_insert(self, tip: TranslatedTip) -> Optional[str]:
        """Generate INSERT statement for a single tip"""
        # Check for duplicates
        key = (tip.card_id, tip.tip_type.value, list(tip.title_json.values())[0] if tip.title_json else "")
        if key in self.generated_keys:
            return None
        self.generated_keys.add(key)

        # Escape JSON for SQL
        title_json = json.dumps(tip.title_json, ensure_ascii=False).replace("'", "''")
        content_json = json.dumps(tip.content_json, ensure_ascii=False).replace("'", "''")

        icon = f"'{tip.icon}'" if tip.icon else "NULL"

        sql = f"""-- {tip.tip_type.value} tip for card {tip.card_id}
INSERT INTO card_usage_tips (card_id, tip_type, title_json, content_json, icon, priority, is_active)
VALUES (
    {tip.card_id},
    '{tip.tip_type.value}',
    '{title_json}',
    '{content_json}',
    {icon},
    {tip.priority},
    true
) ON DUPLICATE KEY UPDATE
    title_json = VALUES(title_json),
    content_json = VALUES(content_json),
    icon = VALUES(icon),
    priority = VALUES(priority),
    updated_at = NOW();"""

        return sql

    def _generate_reward_info_update(self, info: CardRewardInfo) -> Optional[str]:
        """Generate UPDATE statement for card reward info"""
        updates = []

        if info.reward_type:
            updates.append(f"reward_type = '{info.reward_type.value}'")

        if info.point_value is not None:
            updates.append(f"point_value = {info.point_value:.4f}")

        if info.point_program:
            program = info.point_program.replace("'", "''")
            updates.append(f"point_program = '{program}'")

        if info.transfer_partners:
            partners_json = json.dumps([
                {"partner": p.partner_name, "ratio": p.ratio, "type": p.program_type}
                for p in info.transfer_partners
            ], ensure_ascii=False).replace("'", "''")
            updates.append(f"transfer_partners_json = '{partners_json}'")

        if not updates:
            return None

        updates_str = ',\n    '.join(updates)
        sql = f"""-- Update reward info for card {info.card_id}
UPDATE credit_cards SET
    {updates_str},
    updated_at = NOW()
WHERE id = {info.card_id};"""

        return sql

    def generate_delete_sql(self, card_id: int) -> str:
        """Generate SQL to delete all tips for a card"""
        return f"""-- Delete all tips for card {card_id}
DELETE FROM card_usage_tips WHERE card_id = {card_id};"""

    def generate_full_sql_from_scraped_data(self, data_list: List[ScrapedCardData],
                                             translated_tips: List[TranslatedTip],
                                             output_filename: str = None) -> str:
        """Generate complete SQL from scraped data and translations"""
        # Extract reward infos
        reward_infos = [d.reward_info for d in data_list if d.reward_info]

        return self.generate_sql(translated_tips, reward_infos, output_filename)


class DryRunGenerator:
    """Generator for dry run preview"""

    def preview(self, tips: List[TranslatedTip],
                reward_infos: List[CardRewardInfo] = None) -> str:
        """Generate preview of what would be generated"""
        lines = []
        lines.append("=" * 60)
        lines.append("DRY RUN PREVIEW")
        lines.append("=" * 60)
        lines.append("")

        # Group tips by card
        tips_by_card = {}
        for tip in tips:
            if tip.card_id not in tips_by_card:
                tips_by_card[tip.card_id] = []
            tips_by_card[tip.card_id].append(tip)

        for card_id, card_tips in tips_by_card.items():
            lines.append(f"Card ID: {card_id}")
            lines.append("-" * 40)

            for tip in card_tips:
                en_title = tip.title_json.get("en", "N/A")
                zh_title = tip.title_json.get("zh", "N/A")
                lines.append(f"  [{tip.tip_type.value}] {en_title}")
                lines.append(f"    -> {zh_title}")

            lines.append("")

        if reward_infos:
            lines.append("REWARD INFO UPDATES:")
            lines.append("-" * 40)
            for info in reward_infos:
                lines.append(f"  Card {info.card_id}: {info.reward_type.value}")
                if info.point_program:
                    lines.append(f"    Program: {info.point_program}")
                if info.point_value:
                    lines.append(f"    Value: {info.point_value:.4f}")
                if info.transfer_partners:
                    lines.append(f"    Partners: {len(info.transfer_partners)}")
            lines.append("")

        lines.append("=" * 60)
        lines.append(f"Total tips: {len(tips)}")
        lines.append(f"Total reward updates: {len(reward_infos) if reward_infos else 0}")
        lines.append("=" * 60)

        return "\n".join(lines)
