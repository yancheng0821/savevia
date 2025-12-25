"""
Scraper for bank official websites
"""

import re
from typing import Optional, List
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper
from ..models import (
    ScrapedCardData, UsageTip, CardRewardInfo, TransferPartner,
    TipType, RewardType
)
from ..config import BANK_CONFIGS


class BankScraper(BaseScraper):
    """Scraper for bank official websites based on apply_url"""

    def __init__(self, use_selenium: bool = True):
        super().__init__(use_selenium)
        self.source = "bank_official"

    def scrape_card(self, card_id: int, card_name: str, bank: str,
                    apply_url: Optional[str] = None) -> Optional[ScrapedCardData]:
        """Scrape usage tips from the bank's official card page"""
        if not apply_url:
            print(f"No apply_url for {bank} {card_name}")
            return None

        # Determine which bank configuration to use
        bank_config = self._get_bank_config(apply_url, bank)
        if not bank_config:
            print(f"No configuration for bank: {bank}")
            return None

        soup = self.get_soup(apply_url, wait_selector="body")
        if not soup:
            return None

        data = ScrapedCardData(
            card_id=card_id,
            card_name=card_name,
            bank=bank,
            source=f"{bank.lower()}_official"
        )

        # Extract benefits/features
        benefits = self._extract_benefits(soup, bank_config)
        for i, (title, content) in enumerate(benefits):
            data.usage_tips.append(UsageTip(
                card_id=card_id,
                tip_type=TipType.BEST_USE,
                title_en=title,
                content_en=content,
                icon=self._detect_icon(title, content),
                priority=i,
                source_url=apply_url
            ))

        # Extract rewards information
        rewards = self._extract_rewards(soup, bank_config)
        for i, (title, content) in enumerate(rewards):
            data.usage_tips.append(UsageTip(
                card_id=card_id,
                tip_type=TipType.REDEMPTION,
                title_en=title,
                content_en=content,
                icon="gift",
                priority=i,
                source_url=apply_url
            ))

        # Extract reward info (point value, program, etc.)
        data.reward_info = self._extract_reward_info(soup, card_id, bank)

        return data if data.usage_tips else None

    def scrape_all(self, cards: List[dict]) -> List[ScrapedCardData]:
        """Scrape usage tips for all provided cards from bank websites"""
        results = []

        with self:
            for card in cards:
                card_id = card.get('id')
                card_name = card.get('name', '')
                bank = card.get('bank', '')
                apply_url = card.get('apply_url')

                if not apply_url:
                    continue

                print(f"Scraping bank page: {bank} {card_name}...")
                try:
                    data = self.scrape_card(card_id, card_name, bank, apply_url)
                    if data:
                        results.append(data)
                        print(f"  Found {len(data.usage_tips)} tips")
                    else:
                        print(f"  No data found")
                except Exception as e:
                    print(f"  Error: {e}")

        return results

    def _get_bank_config(self, url: str, bank: str) -> Optional[dict]:
        """Get bank-specific configuration based on URL or bank name"""
        # First try to match by URL domain
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        for bank_key, config in BANK_CONFIGS.items():
            if config["domain"] in domain:
                return config

        # Fall back to bank name matching
        bank_upper = bank.upper()
        if bank_upper in BANK_CONFIGS:
            return BANK_CONFIGS[bank_upper]

        # Return a generic config
        return {
            "domain": domain,
            "card_page_selectors": {
                "benefits": ".benefits, .features, .card-benefits, .card-features, [class*='benefit'], [class*='feature']",
                "rewards": ".rewards, .earn, .points, [class*='reward'], [class*='earn']",
                "terms": ".terms, .legal, .disclosure"
            }
        }

    def _extract_benefits(self, soup: BeautifulSoup, config: dict) -> List[tuple]:
        """Extract benefits/features from bank page"""
        benefits = []
        selectors = config.get("card_page_selectors", {}).get("benefits", "")

        for selector in selectors.split(", "):
            elements = soup.select(f"{selector} li, {selector} p, {selector} div")
            for elem in elements:
                text = elem.get_text(strip=True)
                if text and len(text) > 20 and len(text) < 500:
                    # Skip navigation, footer, legal text
                    if self._is_valid_content(text):
                        title, content = self._split_title_content(text)
                        if (title, content) not in benefits:
                            benefits.append((title, content))

            if benefits:
                break

        return benefits[:6]  # Limit to 6 benefits

    def _extract_rewards(self, soup: BeautifulSoup, config: dict) -> List[tuple]:
        """Extract rewards information from bank page"""
        rewards = []
        selectors = config.get("card_page_selectors", {}).get("rewards", "")

        for selector in selectors.split(", "):
            elements = soup.select(f"{selector} li, {selector} p")
            for elem in elements:
                text = elem.get_text(strip=True)
                if text and len(text) > 20 and len(text) < 500:
                    text_lower = text.lower()
                    # Only include if it's about rewards/points
                    if any(kw in text_lower for kw in ['earn', 'point', 'reward', 'redeem', 'cashback', 'cash back', 'bonus']):
                        if self._is_valid_content(text):
                            title, content = self._split_title_content(text)
                            if (title, content) not in rewards:
                                rewards.append((title, content))

            if rewards:
                break

        return rewards[:4]  # Limit to 4 reward tips

    def _extract_reward_info(self, soup: BeautifulSoup, card_id: int, bank: str) -> Optional[CardRewardInfo]:
        """Extract reward type and point program information"""
        text = soup.get_text().lower()

        reward_type = RewardType.CASHBACK
        point_value = None
        point_program = None
        transfer_partners = []

        # Determine reward type and program
        if 'aeroplan' in text:
            reward_type = RewardType.POINTS
            point_program = "Aeroplan"
        elif 'scene+' in text or 'scene plus' in text:
            reward_type = RewardType.POINTS
            point_program = "Scene+"
        elif 'membership rewards' in text or 'mr points' in text:
            reward_type = RewardType.POINTS
            point_program = "Membership Rewards"
        elif 'avion' in text:
            reward_type = RewardType.POINTS
            point_program = "RBC Avion"
        elif 'td rewards' in text:
            reward_type = RewardType.POINTS
            point_program = "TD Rewards"
        elif 'point' in text or 'mile' in text:
            reward_type = RewardType.POINTS

        # Try to extract point value
        value_patterns = [
            r'(\d+\.?\d*)\s*(?:cent|¢|cents)\s*(?:per|/|each)\s*point',
            r'point\s*(?:is\s*)?worth\s*(\d+\.?\d*)\s*(?:cent|¢)',
            r'(\d+\.?\d*)%\s*value',
        ]

        for pattern in value_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    point_value = float(match.group(1)) / 100
                    break
                except ValueError:
                    pass

        # Extract transfer partners for point programs
        if point_program:
            transfer_partners = self._extract_transfer_partners(soup, point_program)

        if reward_type != RewardType.CASHBACK or point_value or point_program:
            return CardRewardInfo(
                card_id=card_id,
                reward_type=reward_type,
                point_value=point_value,
                point_program=point_program,
                transfer_partners=transfer_partners
            )

        return None

    def _extract_transfer_partners(self, soup: BeautifulSoup, program: str) -> List[TransferPartner]:
        """Extract transfer partner information"""
        partners = []
        text = soup.get_text().lower()

        # Known transfer partner keywords
        partner_keywords = {
            "Aeroplan": [
                ("air canada", "1:1", "AIRLINE"),
                ("star alliance", "1:1", "AIRLINE"),
                ("marriott", "1:1", "HOTEL"),
            ],
            "Membership Rewards": [
                ("aeroplan", "1:1", "AIRLINE"),
                ("british airways", "1:1", "AIRLINE"),
                ("hilton", "1:2", "HOTEL"),
                ("marriott", "1:1", "HOTEL"),
            ],
            "Scene+": [
                ("empire", "varies", "RETAIL"),
                ("cineplex", "varies", "ENTERTAINMENT"),
            ]
        }

        if program in partner_keywords:
            for partner_name, ratio, partner_type in partner_keywords[program]:
                if partner_name in text:
                    partners.append(TransferPartner(
                        partner_name=partner_name.title(),
                        ratio=ratio,
                        program_type=partner_type
                    ))

        return partners

    def _is_valid_content(self, text: str) -> bool:
        """Check if text is valid content (not navigation, footer, etc.)"""
        text_lower = text.lower()

        # Skip common non-content patterns
        skip_patterns = [
            'cookie', 'privacy', 'copyright', '©',
            'sign in', 'log in', 'register', 'apply now',
            'terms and conditions', 'legal',
            'follow us', 'contact us', 'about us',
            'all rights reserved'
        ]

        for pattern in skip_patterns:
            if pattern in text_lower:
                return False

        return True

    def _split_title_content(self, text: str) -> tuple:
        """Split text into title and content"""
        for sep in [':', ' - ', ' – ', '. ']:
            if sep in text:
                parts = text.split(sep, 1)
                if len(parts) == 2 and 5 < len(parts[0]) < 60:
                    return parts[0].strip(), parts[1].strip()

        # Use first sentence or phrase as title
        words = text.split()
        if len(words) > 6:
            title = ' '.join(words[:6]) + '...'
            return title, text

        return text, text

    def _detect_icon(self, title: str, content: str) -> str:
        """Detect appropriate icon based on content"""
        text = (title + ' ' + content).lower()

        icon_keywords = {
            'dining': ['dining', 'restaurant', 'food', 'eat', 'meal'],
            'grocery': ['grocery', 'groceries', 'supermarket'],
            'gas': ['gas', 'fuel', 'petrol'],
            'travel': ['travel', 'hotel', 'flight', 'airline', 'airport', 'vacation'],
            'streaming': ['streaming', 'netflix', 'spotify'],
            'shopping': ['shopping', 'online', 'amazon', 'retail'],
            'transit': ['transit', 'uber', 'lyft', 'public transport'],
            'insurance': ['insurance', 'protection', 'warranty'],
            'lounge': ['lounge', 'airport lounge', 'priority pass'],
        }

        for icon, keywords in icon_keywords.items():
            for kw in keywords:
                if kw in text:
                    return icon

        return 'default'
