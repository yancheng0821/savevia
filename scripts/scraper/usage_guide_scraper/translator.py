"""
OpenAI-based translator for multi-language content
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import asdict

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI not installed. Run: pip install openai")

from .config import (
    OPENAI_API_KEY, OPENAI_MODEL, LANGUAGES, LANGUAGE_NAMES,
    CACHE_DIR, TRANSLATION_PROMPT
)
from .models import UsageTip, TranslatedTip


class TranslationCache:
    """Simple file-based translation cache"""

    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_file = cache_dir / "translation_cache.json"
        self._cache = self._load_cache()

    def _load_cache(self) -> dict:
        """Load cache from file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Warning: Could not save cache: {e}")

    def _get_key(self, title: str, content: str) -> str:
        """Generate cache key from content"""
        combined = f"{title}|||{content}"
        return hashlib.md5(combined.encode()).hexdigest()

    def get(self, title: str, content: str) -> Optional[dict]:
        """Get cached translation"""
        key = self._get_key(title, content)
        return self._cache.get(key)

    def set(self, title: str, content: str, translation: dict):
        """Cache a translation"""
        key = self._get_key(title, content)
        self._cache[key] = translation
        self._save_cache()


class Translator:
    """OpenAI-based translator for usage tips"""

    def __init__(self, api_key: str = OPENAI_API_KEY, use_cache: bool = True):
        if not OPENAI_AVAILABLE:
            raise RuntimeError("OpenAI package not installed")

        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=api_key)
        self.model = OPENAI_MODEL
        self.cache = TranslationCache() if use_cache else None
        self.target_languages = [lang for lang in LANGUAGES if lang != "en"]

    def translate_tip(self, tip: UsageTip) -> TranslatedTip:
        """Translate a single usage tip to all target languages"""
        # Check cache first
        if self.cache:
            cached = self.cache.get(tip.title_en, tip.content_en)
            if cached:
                return TranslatedTip.from_usage_tip(
                    tip,
                    cached.get("title", {}),
                    cached.get("content", {})
                )

        # Call OpenAI for translation
        try:
            translations = self._translate_with_openai(tip.title_en, tip.content_en)
        except Exception as e:
            print(f"Translation error: {e}")
            # Return with empty translations (English only)
            return TranslatedTip.from_usage_tip(tip, {}, {})

        # Cache the result
        if self.cache:
            self.cache.set(tip.title_en, tip.content_en, translations)

        return TranslatedTip.from_usage_tip(
            tip,
            translations.get("title", {}),
            translations.get("content", {})
        )

    def translate_tips(self, tips: List[UsageTip]) -> List[TranslatedTip]:
        """Translate multiple tips"""
        results = []
        total = len(tips)

        for i, tip in enumerate(tips, 1):
            print(f"  Translating {i}/{total}: {tip.title_en[:40]}...")
            translated = self.translate_tip(tip)
            results.append(translated)

        return results

    def _translate_with_openai(self, title: str, content: str) -> dict:
        """Call OpenAI API to translate content"""
        target_lang_str = ", ".join([
            LANGUAGE_NAMES.get(lang, lang) for lang in self.target_languages
        ])

        prompt = TRANSLATION_PROMPT.format(
            target_languages=target_lang_str,
            title=title,
            content=content
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional translator. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=2000
        )

        result_text = response.choices[0].message.content.strip()

        # Parse JSON response
        try:
            # Handle potential markdown code blocks
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
                result_text = result_text.strip()

            return json.loads(result_text)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Raw response: {result_text[:500]}")
            return {"title": {}, "content": {}}

    def batch_translate(self, tips: List[UsageTip], batch_size: int = 5) -> List[TranslatedTip]:
        """Translate tips in batches for efficiency"""
        results = []
        total = len(tips)

        for i in range(0, total, batch_size):
            batch = tips[i:i + batch_size]
            print(f"Translating batch {i // batch_size + 1}/{(total + batch_size - 1) // batch_size}...")

            for tip in batch:
                # Check cache first
                if self.cache:
                    cached = self.cache.get(tip.title_en, tip.content_en)
                    if cached:
                        results.append(TranslatedTip.from_usage_tip(
                            tip,
                            cached.get("title", {}),
                            cached.get("content", {})
                        ))
                        continue

                # Translate and cache
                translated = self.translate_tip(tip)
                results.append(translated)

        return results


class MockTranslator:
    """Mock translator for testing without API calls"""

    def translate_tip(self, tip: UsageTip) -> TranslatedTip:
        """Return tip with placeholder translations"""
        translations = {}
        for lang in ["zh", "fr", "es", "ja", "ko"]:
            translations[lang] = f"[{lang.upper()}] {tip.title_en}"

        content_translations = {}
        for lang in ["zh", "fr", "es", "ja", "ko"]:
            content_translations[lang] = f"[{lang.upper()}] {tip.content_en}"

        return TranslatedTip.from_usage_tip(tip, translations, content_translations)

    def translate_tips(self, tips: List[UsageTip]) -> List[TranslatedTip]:
        """Translate multiple tips with mock translations"""
        return [self.translate_tip(tip) for tip in tips]

    def batch_translate(self, tips: List[UsageTip], batch_size: int = 5) -> List[TranslatedTip]:
        """Batch translate with mock translations"""
        return self.translate_tips(tips)
