"""
AI-powered scraper that uses OpenAI to extract structured tips from credit card pages
"""

import json
import re
import time
import hashlib
from typing import Optional, List, Dict, Any
from pathlib import Path

from .base_scraper import BaseScraper
from ..models import (
    ScrapedCardData, UsageTip, TipType
)
from ..config import (
    REVIEW_SITES, POT_CARD_SLUGS, NERDWALLET_CARD_SLUGS,
    CCG_CARD_SLUGS, RATEHUB_CARD_SLUGS,
    AI_EXTRACTION_PROMPT, OPENAI_API_KEY, OPENAI_MODEL, CACHE_DIR
)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai not installed. Run: pip install openai")


class AICardScraper(BaseScraper):
    """AI-powered scraper that extracts structured tips using OpenAI"""

    def __init__(self, use_selenium: bool = True, use_cache: bool = True):
        super().__init__(use_selenium)
        self.source = "ai_extraction"
        self.use_cache = use_cache
        self.cache_dir = CACHE_DIR / "ai_extractions"
        self.cache_dir.mkdir(exist_ok=True)

        if OPENAI_AVAILABLE and OPENAI_API_KEY:
            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        else:
            self.client = None
            print("Warning: OpenAI not available or API key not set")

    def _get_cache_key(self, card_id: int, content_hash: str) -> str:
        """Generate cache key for a card extraction"""
        return f"{card_id}_{content_hash}"

    def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached extraction result"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def _save_to_cache(self, cache_key: str, result: Dict):
        """Save extraction result to cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save cache: {e}")

    def _get_all_urls_for_card(self, card_id: int, card_name: str, bank: str) -> List[str]:
        """Get all possible URLs for a card from different sources"""
        urls = []

        # Prince of Travel
        if card_id in POT_CARD_SLUGS:
            slug = POT_CARD_SLUGS[card_id]
            urls.append(f"{REVIEW_SITES['princeoftravel']['base_url']}/credit-cards/{slug}")

        # NerdWallet
        if card_id in NERDWALLET_CARD_SLUGS:
            slug = NERDWALLET_CARD_SLUGS[card_id]
            urls.append(f"{REVIEW_SITES['nerdwallet']['base_url']}/p/reviews/credit-cards/{slug}")

        # Credit Card Genius
        if card_id in CCG_CARD_SLUGS:
            slug = CCG_CARD_SLUGS[card_id]
            urls.append(f"{REVIEW_SITES['creditcardgenius']['base_url']}/credit-cards/{slug}")

        # Ratehub
        if card_id in RATEHUB_CARD_SLUGS:
            slug = RATEHUB_CARD_SLUGS[card_id]
            urls.append(f"{REVIEW_SITES['ratehub']['base_url']}/credit-cards/card/{slug}")

        return urls

    def _extract_page_content(self, soup) -> str:
        """Extract relevant text content from page, removing navigation and ads"""
        if not soup:
            return ""

        # Remove script and style elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()

        # Remove common ad/navigation classes
        for selector in ['.ad', '.advertisement', '.sidebar', '.menu', '.nav',
                        '.cookie', '.popup', '.modal', '[class*="social"]']:
            for element in soup.select(selector):
                element.decompose()

        # Get main content areas
        main_content = []

        # Try to find main content containers
        content_selectors = [
            'article', 'main', '.content', '.post-content', '.entry-content',
            '.review-content', '.card-details', '[class*="review"]', '[class*="content"]'
        ]

        for selector in content_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(separator=' ', strip=True)
                if len(text) > 200:  # Only include substantial content
                    main_content.append(text)

        # Fallback to body if no main content found
        if not main_content:
            body = soup.find('body')
            if body:
                main_content.append(body.get_text(separator=' ', strip=True))

        # Combine and clean content
        combined = ' '.join(main_content)
        # Remove excessive whitespace
        combined = re.sub(r'\s+', ' ', combined)
        # Truncate if too long (OpenAI has token limits)
        if len(combined) > 15000:
            combined = combined[:15000] + "..."

        return combined

    def _call_openai(self, card_name: str, bank: str, content: str) -> Optional[Dict]:
        """Call OpenAI API to extract structured tips"""
        if not self.client:
            print("OpenAI client not available")
            return None

        prompt = AI_EXTRACTION_PROMPT.format(
            card_name=card_name,
            bank=bank,
            content=content
        )

        try:
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert credit card analyst. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            result_text = response.choices[0].message.content.strip()

            # Try to extract JSON from response
            # Sometimes the model wraps it in markdown code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(1)

            # Parse JSON
            result = json.loads(result_text)
            return result

        except json.JSONDecodeError as e:
            print(f"Failed to parse OpenAI response as JSON: {e}")
            print(f"Response was: {result_text[:500]}...")
            return None
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

    def _parse_tips(self, card_id: int, card_name: str, bank: str,
                    ai_result: Dict, source_url: str) -> List[UsageTip]:
        """Parse AI extraction result into UsageTip objects"""
        tips = []

        if not ai_result or 'tips' not in ai_result:
            return tips

        for tip_data in ai_result.get('tips', []):
            try:
                # Map type string to TipType enum
                type_str = tip_data.get('type', 'BEST_USE').upper()
                try:
                    tip_type = TipType(type_str)
                except ValueError:
                    tip_type = TipType.BEST_USE

                tip = UsageTip(
                    card_id=card_id,
                    tip_type=tip_type,
                    title_en=tip_data.get('title', '')[:100],  # Truncate if too long
                    content_en=tip_data.get('content', '')[:300],
                    icon=tip_data.get('icon', 'default'),
                    priority=tip_data.get('priority', 5),
                    source_url=source_url,
                    card_name=card_name,
                    bank=bank
                )
                tips.append(tip)
            except Exception as e:
                print(f"Error parsing tip: {e}")
                continue

        return tips

    def scrape_card(self, card_id: int, card_name: str, bank: str,
                    apply_url: Optional[str] = None) -> Optional[ScrapedCardData]:
        """Scrape and extract tips for a specific card using AI"""

        urls = self._get_all_urls_for_card(card_id, card_name, bank)
        if not urls:
            print(f"  No URLs configured for card_id={card_id}")
            return None

        all_content = []
        successful_urls = []

        # Collect content from all available sources
        for url in urls:
            print(f"  Fetching: {url}")
            soup = self.get_soup(url, wait_selector="body", wait_time=3)
            if soup:
                content = self._extract_page_content(soup)
                if content and len(content) > 500:
                    all_content.append(content)
                    successful_urls.append(url)
                    print(f"    Got {len(content)} chars")
                else:
                    print(f"    Content too short or empty")
            else:
                print(f"    Failed to fetch")
            time.sleep(1)  # Small delay between requests

        if not all_content:
            print(f"  No content collected for {card_name}")
            return None

        # Combine content from all sources
        combined_content = "\n\n---SOURCE BREAK---\n\n".join(all_content)

        # Check cache
        content_hash = hashlib.md5(combined_content.encode()).hexdigest()[:12]
        cache_key = self._get_cache_key(card_id, content_hash)

        if self.use_cache:
            cached = self._get_cached_result(cache_key)
            if cached:
                print(f"  Using cached AI extraction")
                ai_result = cached
            else:
                print(f"  Calling OpenAI for extraction...")
                ai_result = self._call_openai(card_name, bank, combined_content)
                if ai_result:
                    self._save_to_cache(cache_key, ai_result)
        else:
            print(f"  Calling OpenAI for extraction...")
            ai_result = self._call_openai(card_name, bank, combined_content)

        if not ai_result:
            return None

        # Parse tips
        tips = self._parse_tips(card_id, card_name, bank, ai_result, successful_urls[0] if successful_urls else "")

        if not tips:
            return None

        data = ScrapedCardData(
            card_id=card_id,
            card_name=card_name,
            bank=bank,
            usage_tips=tips,
            source=self.source
        )

        return data

    def scrape_all(self, cards: List[dict]) -> List[ScrapedCardData]:
        """Scrape tips for all provided cards using AI extraction"""
        results = []

        with self:
            for card in cards:
                card_id = card.get('id')
                card_name = card.get('name', '')
                bank = card.get('bank', '')

                print(f"\nProcessing: {bank} {card_name} (id={card_id})")
                try:
                    data = self.scrape_card(card_id, card_name, bank)
                    if data:
                        results.append(data)
                        print(f"  Extracted {len(data.usage_tips)} tips")
                    else:
                        print(f"  No tips extracted")
                except Exception as e:
                    print(f"  Error: {e}")

                # Delay between cards
                time.sleep(2)

        return results


class SingleSourceAIScraper(AICardScraper):
    """AI scraper that fetches from a single specified source"""

    def __init__(self, source_name: str, use_selenium: bool = True, use_cache: bool = True):
        super().__init__(use_selenium, use_cache)
        self.source_name = source_name
        self.source = f"ai_{source_name}"

    def _get_all_urls_for_card(self, card_id: int, card_name: str, bank: str) -> List[str]:
        """Get URL from the specified source only"""
        slug_maps = {
            'princeoftravel': (POT_CARD_SLUGS, REVIEW_SITES['princeoftravel']['base_url'] + '/credit-cards/'),
            'nerdwallet': (NERDWALLET_CARD_SLUGS, REVIEW_SITES['nerdwallet']['base_url'] + '/p/reviews/credit-cards/'),
            'creditcardgenius': (CCG_CARD_SLUGS, REVIEW_SITES['creditcardgenius']['base_url'] + '/credit-cards/'),
            'ratehub': (RATEHUB_CARD_SLUGS, REVIEW_SITES['ratehub']['base_url'] + '/credit-cards/card/'),
        }

        if self.source_name not in slug_maps:
            return []

        slug_map, base_url = slug_maps[self.source_name]

        if card_id in slug_map:
            return [base_url + slug_map[card_id]]

        return []
