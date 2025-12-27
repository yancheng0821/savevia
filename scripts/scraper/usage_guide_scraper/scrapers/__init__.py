"""
Scrapers for different data sources
"""

from .base_scraper import BaseScraper
from .review_site_scraper import CreditCardGeniusUsageScraper, RatehubUsageScraper
from .bank_scraper import BankScraper
from .ai_scraper import AICardScraper, SingleSourceAIScraper

__all__ = [
    'BaseScraper',
    'CreditCardGeniusUsageScraper',
    'RatehubUsageScraper',
    'BankScraper',
    'AICardScraper',
    'SingleSourceAIScraper'
]
