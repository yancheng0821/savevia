"""
Scrapers for credit card review sites (creditcardgenius.ca, ratehub.ca)
"""

import re
import time
from typing import Optional, List
from bs4 import BeautifulSoup, Tag

from .base_scraper import BaseScraper
from ..models import (
    ScrapedCardData, UsageTip, CardRewardInfo, TransferPartner,
    TipType, RewardType, get_tip_icon
)
from ..config import REVIEW_SITES, CCG_CARD_SLUGS, RATEHUB_CARD_SLUGS


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
        search_url = self._build_search_url(card_id, card_name, bank)
        if not search_url:
            print(f"  No URL mapping for card_id={card_id}")
            return None

        soup = self.get_soup(search_url, wait_selector="body", wait_time=3)
        if not soup:
            return None

        data = ScrapedCardData(
            card_id=card_id,
            card_name=card_name,
            bank=bank,
            source=self.source
        )

        # Extract page text for analysis
        page_text = soup.get_text(separator=' ', strip=True)

        # Extract pros as BEST_USE tips
        pros = self._extract_pros(soup, page_text)
        for i, (title, content) in enumerate(pros):
            data.usage_tips.append(UsageTip(
                card_id=card_id,
                tip_type=TipType.BEST_USE,
                title_en=title,
                content_en=content,
                icon=self._detect_icon(title, content),
                priority=i,
                source_url=search_url,
                card_name=card_name,
                bank=bank
            ))

        # Extract cons as AVOID tips
        cons = self._extract_cons(soup, page_text)
        for i, (title, content) in enumerate(cons):
            data.usage_tips.append(UsageTip(
                card_id=card_id,
                tip_type=TipType.AVOID,
                title_en=title,
                content_en=content,
                icon="warning",
                priority=i,
                source_url=search_url,
                card_name=card_name,
                bank=bank
            ))

        # Extract redemption tips
        redemption_tips = self._extract_redemption_info(soup, page_text)
        for i, (title, content) in enumerate(redemption_tips):
            data.usage_tips.append(UsageTip(
                card_id=card_id,
                tip_type=TipType.REDEMPTION,
                title_en=title,
                content_en=content,
                icon="gift",
                priority=i,
                source_url=search_url,
                card_name=card_name,
                bank=bank
            ))

        # Extract reward info
        data.reward_info = self._extract_reward_info(soup, card_id, card_name, bank)

        return data if data.usage_tips else None

    def scrape_all(self, cards: List[dict]) -> List[ScrapedCardData]:
        """Scrape usage tips for all provided cards"""
        results = []

        with self:
            for card in cards:
                card_id = card.get('id')
                card_name = card.get('name', '')
                bank = card.get('bank', '')

                print(f"Scraping CCG: {bank} {card_name}...")
                try:
                    data = self.scrape_card(card_id, card_name, bank)
                    if data:
                        results.append(data)
                        print(f"  Found {len(data.usage_tips)} tips")
                    else:
                        print(f"  No data found")
                except Exception as e:
                    print(f"  Error: {e}")

                # Delay between requests
                time.sleep(2)

        return results

    def _build_search_url(self, card_id: int, card_name: str, bank: str) -> Optional[str]:
        """Build the search URL for a card using slug mapping"""
        # First try the explicit slug mapping
        if card_id in CCG_CARD_SLUGS:
            slug = CCG_CARD_SLUGS[card_id]
            return f"{self.BASE_URL}/credit-cards/{slug}"

        # Fallback: generate slug from card name and bank
        full_name = f"{bank} {card_name}".lower()
        # Remove special characters and normalize
        slug = re.sub(r'[^\w\s-]', '', full_name)
        slug = re.sub(r'\s+', '-', slug.strip())
        slug = re.sub(r'-+', '-', slug)

        return f"{self.BASE_URL}/credit-cards/{slug}"

    def _extract_pros(self, soup: BeautifulSoup, page_text: str = "") -> List[tuple]:
        """Extract pros/advantages from the page"""
        pros = []
        seen_texts = set()

        # Try different selectors for pros section (updated for CCG)
        # CCG uses colors: green (#2ecc71) for positive
        selectors = [
            '[style*="color: #2ecc71"], [style*="color:#2ecc71"]',
            '[class*="positive"] li, [class*="Positive"] li',
            '[class*="pros"] li, [class*="Pros"] li',
            '.pros-section li, .advantages li',
            '.card-pros li, .benefits li',
        ]

        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 15 and text not in seen_texts:
                        if self._is_valid_tip_content(text):
                            title, content = self._split_title_content(text)
                            pros.append((title, content))
                            seen_texts.add(text)
                if pros:
                    break

        # Fallback: Extract from page text using patterns
        if not pros and page_text:
            pros = self._extract_from_text(page_text, is_pro=True)

        return pros[:5]  # Limit to 5 pros

    def _extract_cons(self, soup: BeautifulSoup, page_text: str = "") -> List[tuple]:
        """Extract cons/disadvantages from the page"""
        cons = []
        seen_texts = set()

        # Try different selectors (updated for CCG)
        # CCG uses colors: red (#d9534f) for negative
        selectors = [
            '[style*="color: #d9534f"], [style*="color:#d9534f"]',
            '[class*="negative"] li, [class*="Negative"] li',
            '[class*="cons"] li, [class*="Cons"] li',
            '.cons-section li, .disadvantages li',
            '.card-cons li, .drawbacks li',
        ]

        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 15 and text not in seen_texts:
                        if self._is_valid_tip_content(text):
                            title, content = self._split_title_content(text)
                            cons.append((title, content))
                            seen_texts.add(text)
                if cons:
                    break

        # Fallback: Extract from page text (only specific cons patterns)
        if not cons and page_text:
            cons = self._extract_from_text(page_text, is_pro=False)

        return cons[:3]  # Limit to 3 cons

    def _extract_from_text(self, page_text: str, is_pro: bool = True) -> List[tuple]:
        """Extract pros or cons from raw page text using pattern matching"""
        results = []
        text_lower = page_text.lower()

        if is_pro:
            # Look for earning patterns
            patterns = [
                (r'earn\s+(\d+)x?\s+(?:points?|miles?|cashback|cash back)\s+(?:on|at|for)\s+([^.]{10,100})', "High Rewards"),
                (r'(\d+)%\s+(?:cashback|cash back)\s+(?:on|at|for)\s+([^.]{10,100})', "Cash Back"),
                (r'no\s+annual\s+fee', "No Annual Fee"),
                (r'no\s+foreign\s+transaction\s+fee', "No FX Fee"),
                (r'welcome\s+(?:bonus|offer)\s+(?:of\s+)?([^.]{10,80})', "Welcome Bonus"),
                (r'airport\s+lounge\s+access', "Lounge Access"),
                (r'travel\s+(?:medical\s+)?insurance[^.]{0,50}', "Travel Insurance"),
            ]
            for pattern, title in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    if len(match.groups()) > 0:
                        content = match.group(0).strip()
                    else:
                        content = title
                    # Clean up and validate content
                    content = content[:200] if len(content) > 200 else content
                    if self._is_valid_tip_content(content):
                        results.append((title, content.capitalize()))
        else:
            # Look for cons patterns
            patterns = [
                (r'foreign\s+transaction\s+fee\s+(?:of\s+)?(\d+\.?\d*%?)', "Foreign Transaction Fee"),
                (r'(?:annual|yearly)\s+fee\s+(?:of\s+)?\$?(\d+)', "Annual Fee"),
                (r'not\s+(?:widely\s+)?accepted\s+(?:at\s+)?([^.]{5,50})', "Limited Acceptance"),
                (r'minimum\s+(?:personal\s+)?income\s+(?:requirement\s+)?(?:of\s+)?\$?(\d+)', "Income Requirement"),
                (r'no\s+lounge\s+access', "No Lounge Access"),
            ]
            for pattern, title in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    content = match.group(0).strip()
                    content = content[:200] if len(content) > 200 else content
                    if self._is_valid_tip_content(content):
                        results.append((title, content.capitalize()))

        return results[:5]

    def _is_valid_tip_content(self, text: str) -> bool:
        """Check if the extracted content is valid and not navigation/garbage"""
        text_lower = text.lower()

        # Skip common navigation/garbage patterns
        skip_patterns = [
            'mortgage', 'visit', 'page', 'menu', 'login', 'sign in', 'register',
            'cookie', 'privacy', 'terms', 'copyright', 'all rights',
            'navigation', 'footer', 'header', 'sidebar',
            'click here', 'learn more', 'read more', 'see all',
        ]

        for pattern in skip_patterns:
            if pattern in text_lower:
                return False

        # Content should have reasonable length
        if len(text) < 10 or len(text) > 300:
            return False

        return True

    def _extract_redemption_info(self, soup: BeautifulSoup, page_text: str = "") -> List[tuple]:
        """Extract points redemption information"""
        redemption = []

        # Try different selectors
        selectors = [
            '.redemption-section, .points-section, .rewards-section',
            '[class*="redemption"], [class*="Redemption"]',
            '[class*="rewards"], [class*="Rewards"]',
            '.earn-section, .points-value'
        ]

        for selector in selectors:
            section = soup.select_one(selector)
            if section:
                text = section.get_text(strip=True)
                if 'point' in text.lower() or 'redeem' in text.lower():
                    items = section.select('li, p')
                    for item in items[:5]:
                        item_text = item.get_text(strip=True)
                        if len(item_text) > 20:
                            title, content = self._split_title_content(item_text)
                            if 'point' in content.lower() or 'redeem' in content.lower():
                                redemption.append((title, content))
                if redemption:
                    break

        # Fallback: Extract from page text
        if not redemption and page_text:
            text_lower = page_text.lower()
            patterns = [
                (r'transfer\s+(?:points?\s+)?(?:to\s+)?([^.]+aeroplan[^.]*)', "Transfer to Aeroplan"),
                (r'redeem\s+(?:points?\s+)?(?:for\s+)?([^.]+)', "Redemption Options"),
                (r'points?\s+(?:are\s+)?worth\s+(\d+\.?\d*)\s*(?:cents?|¢)', "Point Value"),
            ]
            for pattern, title in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    content = match.group(0).strip()[:200]
                    redemption.append((title, content.capitalize()))

        return redemption[:3]  # Limit to 3 redemption tips

    def _extract_reward_info(self, soup: BeautifulSoup, card_id: int,
                              card_name: str = None, bank: str = None) -> Optional[CardRewardInfo]:
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
                point_program=point_program,
                card_name=card_name,
                bank=bank
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
        search_url = self._build_search_url(card_id, card_name, bank)
        if not search_url:
            print(f"  No URL mapping for card_id={card_id}")
            return None

        soup = self.get_soup(search_url, wait_selector="body", wait_time=3)
        if not soup:
            return None

        data = ScrapedCardData(
            card_id=card_id,
            card_name=card_name,
            bank=bank,
            source=self.source
        )

        # Extract page text for analysis
        page_text = soup.get_text(separator=' ', strip=True)

        # Extract features as BEST_USE tips
        features = self._extract_features(soup, page_text)
        for i, (title, content) in enumerate(features):
            data.usage_tips.append(UsageTip(
                card_id=card_id,
                tip_type=TipType.BEST_USE,
                title_en=title,
                content_en=content,
                icon=self._detect_icon(title, content),
                priority=i,
                source_url=search_url,
                card_name=card_name,
                bank=bank
            ))

        # Extract cons as AVOID tips
        cons = self._extract_cons(soup, page_text)
        for i, (title, content) in enumerate(cons):
            data.usage_tips.append(UsageTip(
                card_id=card_id,
                tip_type=TipType.AVOID,
                title_en=title,
                content_en=content,
                icon="warning",
                priority=i,
                source_url=search_url,
                card_name=card_name,
                bank=bank
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

                # Delay between requests
                time.sleep(2)

        return results

    def _build_search_url(self, card_id: int, card_name: str, bank: str) -> Optional[str]:
        """Build the search URL for a card using slug mapping"""
        # First try the explicit slug mapping
        if card_id in RATEHUB_CARD_SLUGS:
            slug = RATEHUB_CARD_SLUGS[card_id]
            return f"{self.BASE_URL}/credit-cards/card/{slug}"

        # Fallback: generate slug from card name and bank
        full_name = f"{bank} {card_name}".lower()
        slug = re.sub(r'[^\w\s-]', '', full_name)
        slug = re.sub(r'\s+', '-', slug.strip())
        slug = re.sub(r'-+', '-', slug)

        return f"{self.BASE_URL}/credit-cards/card/{slug}"

    def _extract_cons(self, soup: BeautifulSoup, page_text: str = "") -> List[tuple]:
        """Extract cons/drawbacks from Ratehub page"""
        cons = []

        # Look for drawbacks section
        selectors = [
            '[class*="drawback"] li, [class*="Drawback"] li',
            '[class*="con"] li, [class*="Con"] li',
            '[class*="negative"] li, [class*="Negative"] li',
        ]

        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 10 and self._is_valid_tip_content(text):
                        title, content = self._split_title_content(text)
                        cons.append((title, content))
                if cons:
                    break

        # Fallback: Look for patterns in page text
        if not cons and page_text:
            text_lower = page_text.lower()
            patterns = [
                (r'foreign\s+transaction\s+fee\s+(?:of\s+)?(\d+\.?\d*%?)', "Foreign Transaction Fee"),
                (r'(?:annual|yearly)\s+fee\s+(?:of\s+)?\$?(\d+)', "Annual Fee"),
                (r'(?:not|no)\s+(?:widely\s+)?accepted', "Limited Acceptance"),
                (r'minimum\s+(?:personal\s+)?income\s+(?:requirement)?', "Income Requirement"),
            ]
            for pattern, title in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    content = match.group(0).strip()[:200]
                    if self._is_valid_tip_content(content):
                        cons.append((title, content.capitalize()))

        return cons[:3]

    def _extract_features(self, soup: BeautifulSoup, page_text: str = "") -> List[tuple]:
        """Extract card features from Ratehub"""
        features = []

        selectors = [
            '[class*="feature"] li, [class*="Feature"] li',
            '[class*="benefit"] li, [class*="Benefit"] li',
            '[class*="highlight"] li, [class*="Highlight"] li',
            '.card-features li, .features-list li',
            '.key-features li',
        ]

        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 10 and self._is_valid_tip_content(text):
                        title, content = self._split_title_content(text)
                        features.append((title, content))
                if features:
                    break

        # Fallback: Extract from page text using patterns
        if not features and page_text:
            text_lower = page_text.lower()
            patterns = [
                (r'earn\s+(\d+)x?\s+(?:points?|miles?)\s+(?:on|at|for)\s+([^.]{10,100})', "Rewards"),
                (r'(\d+)%\s+(?:cashback|cash back)\s+(?:on|at|for)\s+([^.]{10,100})', "Cash Back"),
                (r'no\s+annual\s+fee', "No Annual Fee"),
                (r'welcome\s+(?:bonus|offer)[^.]{10,80}', "Welcome Bonus"),
                (r'travel\s+(?:medical\s+)?insurance[^.]{0,50}', "Travel Insurance"),
                (r'lounge\s+access', "Lounge Access"),
            ]
            for pattern, title in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    content = match.group(0).strip()[:200]
                    if self._is_valid_tip_content(content):
                        features.append((title, content.capitalize()))

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
            'dining': ['dining', 'restaurant', 'food', 'eat'],
            'grocery': ['grocery', 'groceries', 'supermarket'],
            'gas': ['gas', 'fuel', 'petrol'],
            'travel': ['travel', 'hotel', 'flight', 'airline'],
            'shopping': ['shopping', 'online', 'amazon'],
            'streaming': ['streaming', 'netflix', 'spotify'],
            'transit': ['transit', 'uber', 'lyft'],
            'insurance': ['insurance', 'protection'],
        }

        for icon, keywords in icon_keywords.items():
            for kw in keywords:
                if kw in text:
                    return icon

        return 'default'

    def _is_valid_tip_content(self, text: str) -> bool:
        """Check if the extracted content is valid and not navigation/garbage"""
        text_lower = text.lower()

        # Skip common navigation/garbage patterns
        skip_patterns = [
            'mortgage', 'visit', 'page', 'menu', 'login', 'sign in', 'register',
            'cookie', 'privacy', 'terms', 'copyright', 'all rights',
            'navigation', 'footer', 'header', 'sidebar',
            'click here', 'learn more', 'read more', 'see all',
        ]

        for pattern in skip_patterns:
            if pattern in text_lower:
                return False

        # Content should have reasonable length
        if len(text) < 10 or len(text) > 300:
            return False

        return True
