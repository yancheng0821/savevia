"""
Scrapers for different data sources
"""

from .base_scraper import BaseScraper
from .review_site_scraper import CreditCardGeniusUsageScraper, RatehubUsageScraper
from .bank_scraper import BankScraper

__all__ = [
    'BaseScraper',
    'CreditCardGeniusUsageScraper',
    'RatehubUsageScraper',
    'BankScraper'
]
