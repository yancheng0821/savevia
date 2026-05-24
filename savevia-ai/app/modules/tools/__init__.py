"""Tool registry: TOOLS is the canonical list passed to create_react_agent.

Order mirrors Java's ToolRegistry declaration order (used in system-prompt
listing). The agent itself does not depend on order.
"""

from app.modules.tools.calculate_reward import calculate_reward
from app.modules.tools.compare_cards import compare_cards
from app.modules.tools.get_best_card import get_best_card
from app.modules.tools.get_card_usage_guide import get_card_usage_guide
from app.modules.tools.get_user_cards import get_user_cards
from app.modules.tools.search_cards import search_cards

TOOLS = [
    get_user_cards,
    calculate_reward,
    get_best_card,
    compare_cards,
    get_card_usage_guide,
    search_cards,
]

__all__ = [
    "TOOLS",
    "calculate_reward",
    "compare_cards",
    "get_best_card",
    "get_card_usage_guide",
    "get_user_cards",
    "search_cards",
]
