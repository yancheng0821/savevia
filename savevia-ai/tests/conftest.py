import pytest
import structlog


@pytest.fixture(autouse=True)
def _reset_structlog():
    """Reset structlog defaults between tests to prevent cross-test contamination."""
    structlog.reset_defaults()
    yield
    structlog.reset_defaults()
