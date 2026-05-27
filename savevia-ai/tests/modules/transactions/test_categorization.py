"""Tests for the merchant categorization service."""

from unittest.mock import AsyncMock

import pytest

from app.models.merchant_category import MerchantCategory


@pytest.fixture
def repo():
    return AsyncMock()


def _row(pattern: str, category: str, priority: int = 50, active: bool = True) -> MerchantCategory:
    return MerchantCategory(
        id=1, merchant_pattern=pattern, category=category,
        priority=priority, is_active=active,
    )


def _service(repo):
    from app.modules.transactions.categorization import CategorizationService
    return CategorizationService(merchant_repository=repo)


async def test_returns_other_for_unknown_merchant(repo):
    repo.find_all_active.return_value = [_row("WALMART", "GROCERY")]
    svc = _service(repo)
    await svc.refresh_patterns()
    assert svc.categorize("Random Cafe") == "OTHER"


async def test_returns_other_when_merchant_is_none_or_empty(repo):
    repo.find_all_active.return_value = []
    svc = _service(repo)
    await svc.refresh_patterns()
    assert svc.categorize(None) == "OTHER"
    assert svc.categorize("") == "OTHER"


async def test_matches_case_insensitive_substring(repo):
    repo.find_all_active.return_value = [_row("STARBUCKS", "DINING")]
    svc = _service(repo)
    await svc.refresh_patterns()
    assert svc.categorize("starbucks #4231") == "DINING"
    assert svc.categorize("STARBUCKS DOWNTOWN") == "DINING"


async def test_higher_priority_pattern_wins(repo):
    # Repo returns by priority DESC; mocking the order.
    repo.find_all_active.return_value = [
        _row("AMAZON FRESH", "GROCERY", priority=80),
        _row("AMAZON", "ONLINE_SHOPPING", priority=50),
    ]
    svc = _service(repo)
    await svc.refresh_patterns()
    # "Amazon Fresh" matches the higher-priority specific pattern first
    assert svc.categorize("AMAZON FRESH BC123") == "GROCERY"
    # Plain "Amazon" only matches the lower-priority generic pattern
    assert svc.categorize("AMAZON RETAIL") == "ONLINE_SHOPPING"


async def test_refresh_patterns_picks_up_changes(repo):
    repo.find_all_active.return_value = [_row("PETRO-CANADA", "GAS")]
    svc = _service(repo)
    await svc.refresh_patterns()
    assert svc.categorize("PETRO-CANADA 1234") == "GAS"

    # Reload with new pattern
    repo.find_all_active.return_value = [
        _row("PETRO-CANADA", "GAS"),
        _row("ESSO", "GAS"),
    ]
    await svc.refresh_patterns()
    assert svc.categorize("ESSO STN") == "GAS"


async def test_categorize_with_confidence_higher_priority_higher_confidence(repo):
    repo.find_all_active.return_value = [
        _row("WALMART", "GROCERY", priority=80),
        _row("STORE", "OTHER", priority=10),
    ]
    svc = _service(repo)
    await svc.refresh_patterns()
    out = svc.categorize_with_confidence("WALMART SUPERSTORE")
    # 0.5 + 80/200 = 0.9
    assert out.category == "GROCERY"
    assert out.confidence == 0.9


async def test_categorize_with_confidence_unmatched_returns_lowest(repo):
    repo.find_all_active.return_value = []
    svc = _service(repo)
    await svc.refresh_patterns()
    assert svc.categorize_with_confidence("UNKNOWN").confidence == 0.3
