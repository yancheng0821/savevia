"""
Scrapers for credit card review sites (creditcardgenius.ca, ratehub.ca)
"""

import re
from typing import Optional, List
from bs4 import BeautifulSoup, Tag

from .base_scraper import BaseScraper
from ..models import (
    ScrapedCardData, UsageTip, CardRewardInfo, TransferPartner,
    TipType, RewardType, get_tip_icon
)
from ..config import REVIEW_SITES


class CreditCardGeniusUsageScraper(BaseScraper):
    """Scraper for Credit Card Genius usage tips"""

    BASE_URL = REVIEW_SITES["creditcardgenius"]["base_url"]

    def __init__(self, use_selenium: bool = True):
        super().__init__(use_selenium)
        self.source = "creditcardgenius.ca"

    def scrape_card(self, card_id: int, card_name: str, bank: str,
                    apply_url: Optional[str] = None) -> Optional[ScrapedCardData]:
        """Scrape usage tips for a specific card"""
        # Try to find the card detail page
        search_url = self._build_search_url(card_name, bank)
        if not search_url:
            return None

        soup = self.get_soup(search_url, wait_selector="body")
        if not soup:
            return None

        data = ScrapedCardData(
            card_id=card_id,
            card_name=card_name,
            bank=bank,
            source=self.source
        )

        # Extract pros as BEST_USE tips
        pros = self._extract_pros(soup)
        for i, (title, content) in enumerate(pros):
            data.usage_tips.append(UsageTip(
                card_id=card_id,
                tip_type=TipType.BEST_USE,
                title_en=title,
                content_en=content,
                icon=self._detect_icon(title, content),
                priority=i,
                source_url=search_url
            ))

        # Extract cons as AVOID tips
        cons = self._extract_cons(soup)
        for i, (title, content) in enumerate(cons):
            data.usage_tips.append(UsageTip(
                card_id=card_id,
                tip_type=TipType.AVOID,
                title_en=title,
                content_en=content,
                icon="warning",
                priority=i,
                source_url=search_url
            ))

        # Extract redemption tips
        redemption_tips = self._extract_redemption_info(soup)
        for i, (title, content) in enumerate(redemption_tips):
            data.usage_tips.append(UsageTip(
                card_id=card_id,
                tip_type=TipType.REDEMPTION,
                title_en=title,
                content_en=content,
                icon="gift",
                priority=i,
                source_url=search_url
            ))

        # Extract reward info
        data.reward_info = self._extract_reward_info(soup, card_id)

        return data if data.usage_tips else None

    def scrape_all(self, cards: List[dict]) -> List[ScrapedCardData]:
        """Scrape usage tips for all provided cards"""
        results = []

        with self:
            for card in cards:
                card_id = card.get('id')
                card_name = card.get('name', '')
                bank = card.get('bank', '')

                print(f"Scraping: {bank} {card_name}...")
                try:
                    data = self.scrape_card(card_id, card_name, bank)
                    if data:
                        results.append(data)
                        print(f"  Found {len(data.usage_tips)} tips")
                    else:
                        print(f"  No data found")
                except Exception as e:
                    print(f"  Error: {e}")

        return results

    def _build_search_url(self, card_name: str, bank: str) -> Optional[str]:
        """Build the search URL for a card"""
        # Clean the card name for URL
        slug = re.sub(r'[^\w\s-]', '', card_name.lower())
        slug = re.sub(r'\s+', '-', slug.strip())

        # Try common URL patterns
        bank_slug = bank.lower().replace(' ', '-')

        # Different URL patterns to try
        patterns = [
            f"{self.BASE_URL}/credit-cards/{bank_slug}/{slug}",
            f"{self.BASE_URL}/credit-cards/{slug}",
            f"{self.BASE_URL}/best-credit-cards?search={card_name.replace(' ', '+')}",
        ]

        return patterns[0]  # Start with the most common pattern

    def _extract_pros(self, soup: BeautifulSoup) -> List[tuple]:
        """Extract pros/advantages from the page"""
        pros = []

        # Try different selectors for pros section
        selectors = [
            '.pros-section li, .advantages li',
            '[class*="pros"] li, [class*="advantage"] li',
            '.card-pros li, .benefits li',
            'ul.pros li, ul.advantages li'
        ]

        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 10:
                        # Try to extract title and content
                        title, content = self._split_title_content(text)
                        pros.append((title, content))
                break

        return pros[:5]  # Limit to 5 pros

    def _extract_cons(self, soup: BeautifulSoup) -> List[tuple]:
        """Extract cons/disadvantages from the page"""
        cons = []

        selectors = [
            '.cons-section li, .disadvantages li',
            '[class*="cons"] li, [class*="disadvantage"] li',
            '.card-cons li, .drawbacks li',
            'ul.cons li, ul.disadvantages li'
        ]

        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 10:
                        title, content = self._split_title_content(text)
                        cons.append((title, content))
                break

        return cons[:3]  # Limit to 3 cons

    def _extract_redemption_info(self, soup: BeautifulSoup) -> List[tuple]:
        """Extract points redemption information"""
        redemption = []

        selectors = [
            '.redemption-section, .points-section, .rewards-section',
            '[class*="redemption"], [class*="rewards"]',
            '.earn-section, .points-value'
        ]

        for selector in selectors:
            section = soup.select_one(selector)
            if section:
                # Look for key information
                text = section.get_text(strip=True)
                if 'point' in text.lower() or 'redeem' in text.lower():
                    # Extract bullet points or paragraphs
                    items = section.select('li, p')
                    for item in items[:5]:
                        item_text = item.get_text(strip=True)
                        if len(item_text) > 20:
                            title, content = self._split_title_content(item_text)
                            if 'point' in content.lower() or 'redeem' in content.lower():
                                redemption.append((title, content))
                break

        return redemption[:3]  # Limit to 3 redemption tips

    def _extract_reward_info(self, soup: BeautifulSoup, card_id: int) -> Optional[CardRewardInfo]:
        """Extract reward type and point value information"""
        # Try to find point value
        text = soup.get_text().lower()

        reward_type = RewardType.CASHBACK
        point_value = None
        point_program = None

        if 'point' in text or 'mile' in text:
            reward_type = RewardType.POINTS

            # Try to extract point value
            value_match = re.search(r'(\d+\.?\d*)\s*(?:cent|¢)\s*(?:per|/)\s*point', text)
            if value_match:
                point_value = float(value_match.group(1)) / 100

            # Try to extract program name
            programs = ['aeroplan', 'scene+', 'avion', 'membership rewards', 'td rewards']
            for prog in programs:
                if prog in text:
                    point_program = prog.title()
                    break

        if reward_type != RewardType.CASHBACK or point_value or point_program:
            return CardRewardInfo(
                card_id=card_id,
                reward_type=reward_type,
                point_value=point_value,
                point_program=point_program
            )

        return None

    def _split_title_content(self, text: str) -> tuple:
        """Split text into title and content"""
        # If text has a colon or dash, split on that
        for sep in [':', ' - ', ' – ']:
            if sep in text:
                parts = text.split(sep, 1)
                if len(parts) == 2 and len(parts[0]) < 50:
                    return parts[0].strip(), parts[1].strip()

        # Otherwise, use first sentence as title
        sentences = re.split(r'[.!?]', text, 1)
        if len(sentences) >= 2:
            title = sentences[0].strip()
            content = sentences[1].strip() if sentences[1].strip() else text
            if len(title) < 60:
                return title, content

        # Fallback: first few words as title
        words = text.split()
        if len(words) > 5:
            title = ' '.join(words[:5]) + '...'
            return title, text

        return text, text

    def _detect_icon(self, title: str, content: str) -> str:
        """Detect appropriate icon based on content"""
        text = (title + ' ' + content).lower()

        icon_keywords = {
            'dining': ['dining', 'restaurant', 'food', 'eat'],
            'grocery': ['grocery', 'groceries', 'supermarket'],
            'gas': ['gas', 'fuel', 'petrol'],
            'travel': ['travel', 'hotel', 'flight', 'airline', 'airport'],
            'streaming': ['streaming', 'netflix', 'spotify'],
            'shopping': ['shopping', 'online', 'amazon'],
            'transit': ['transit', 'uber', 'lyft'],
        }

        for icon, keywords in icon_keywords.items():
            for kw in keywords:
                if kw in text:
                    return icon

        return 'default'


class RatehubUsageScraper(BaseScraper):
    """Scraper for Ratehub.ca usage tips"""

    BASE_URL = REVIEW_SITES["ratehub"]["base_url"]

    def __init__(self, use_selenium: bool = True):
        super().__init__(use_selenium)
        self.source = "ratehub.ca"

    def scrape_card(self, card_id: int, card_name: str, bank: str,
                    apply_url: Optional[str] = None) -> Optional[ScrapedCardData]:
        """Scrape usage tips for a specific card from Ratehub"""
        # Similar implementation to CreditCardGenius but with Ratehub-specific selectors
        search_url = self._build_search_url(card_name, bank)
        if not search_url:
            return None

        soup = self.get_soup(search_url, wait_selector="body")
        if not soup:
            return None

        data = ScrapedCardData(
            card_id=card_id,
            card_name=card_name,
            bank=bank,
            source=self.source
        )

        # Extract features as BEST_USE tips
        features = self._extract_features(soup)
        for i, (title, content) in enumerate(features):
            data.usage_tips.append(UsageTip(
                card_id=card_id,
                tip_type=TipType.BEST_USE,
                title_en=title,
                content_en=content,
                icon=self._detect_icon(title, content),
                priority=i,
                source_url=search_url
            ))

        return data if data.usage_tips else None

    def scrape_all(self, cards: List[dict]) -> List[ScrapedCardData]:
        """Scrape usage tips for all provided cards"""
        results = []

        with self:
            for card in cards:
                card_id = card.get('id')
                card_name = card.get('name', '')
                bank = card.get('bank', '')

                print(f"Scraping Ratehub: {bank} {card_name}...")
                try:
                    data = self.scrape_card(card_id, card_name, bank)
                    if data:
                        results.append(data)
                        print(f"  Found {len(data.usage_tips)} tips")
                    else:
                        print(f"  No data found")
                except Exception as e:
                    print(f"  Error: {e}")

        return results

    def _build_search_url(self, card_name: str, bank: str) -> Optional[str]:
        """Build the search URL for a card"""
        slug = re.sub(r'[^\w\s-]', '', card_name.lower())
        slug = re.sub(r'\s+', '-', slug.strip())
        bank_slug = bank.lower().replace(' ', '-')

        return f"{self.BASE_URL}/credit-cards/{bank_slug}/{slug}"

    def _extract_features(self, soup: BeautifulSoup) -> List[tuple]:
        """Extract card features from Ratehub"""
        features = []

        selectors = [
            '.card-features li, .features-list li',
            '[class*="feature"] li, [class*="benefit"] li',
            '.key-features li'
        ]

        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 10:
                        title, content = self._split_title_content(text)
                        features.append((title, content))
                break

        return features[:5]

    def _split_title_content(self, text: str) -> tuple:
        """Split text into title and content"""
        for sep in [':', ' - ', ' – ']:
            if sep in text:
                parts = text.split(sep, 1)
                if len(parts) == 2 and len(parts[0]) < 50:
                    return parts[0].strip(), parts[1].strip()

        words = text.split()
        if len(words) > 5:
            title = ' '.join(words[:5]) + '...'
            return title, text

        return text, text

    def _detect_icon(self, title: str, content: str) -> str:
        """Detect appropriate icon based on content"""
        text = (title + ' ' + content).lower()

        icon_keywords = {
            'dining': ['dining', 'restaurant', 'food'],
            'grocery': ['grocery', 'groceries'],
            'gas': ['gas', 'fuel'],
            'travel': ['travel', 'hotel', 'flight'],
            'shopping': ['shopping', 'online'],
        }

        for icon, keywords in icon_keywords.items():
            for kw in keywords:
                if kw in text:
                    return icon

        return 'default'
