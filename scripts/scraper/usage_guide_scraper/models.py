"""
Data models for usage guide scraper
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class TipType(str, Enum):
    """Types of usage tips"""
    BEST_USE = "BEST_USE"        # 最佳使用场景
    REDEMPTION = "REDEMPTION"    # 积分兑换建议
    STACKING = "STACKING"        # 叠加技巧
    AVOID = "AVOID"              # 避免事项


class RewardType(str, Enum):
    """Types of rewards"""
    CASHBACK = "CASHBACK"
    POINTS = "POINTS"
    MILES = "MILES"


@dataclass
class UsageTip:
    """A single usage tip (in English only, before translation)"""
    card_id: int
    tip_type: TipType
    title_en: str
    content_en: str
    icon: Optional[str] = None
    priority: int = 0
    source_url: Optional[str] = None

    def __hash__(self):
        return hash((self.card_id, self.tip_type.value, self.title_en))

    def __eq__(self, other):
        if not isinstance(other, UsageTip):
            return False
        return (self.card_id == other.card_id and
                self.tip_type == other.tip_type and
                self.title_en == other.title_en)


@dataclass
class TranslatedTip:
    """A usage tip with all language translations"""
    card_id: int
    tip_type: TipType
    title_json: Dict[str, str]   # {"en": "...", "zh": "...", ...}
    content_json: Dict[str, str]  # {"en": "...", "zh": "...", ...}
    icon: Optional[str] = None
    priority: int = 0

    @classmethod
    def from_usage_tip(cls, tip: UsageTip, title_translations: Dict[str, str],
                       content_translations: Dict[str, str]) -> 'TranslatedTip':
        """Create a TranslatedTip from a UsageTip and translations"""
        return cls(
            card_id=tip.card_id,
            tip_type=tip.tip_type,
            title_json={"en": tip.title_en, **title_translations},
            content_json={"en": tip.content_en, **content_translations},
            icon=tip.icon,
            priority=tip.priority
        )


@dataclass
class TransferPartner:
    """A transfer partner for points programs"""
    partner_name: str
    ratio: str  # e.g., "1:1", "1:2"
    program_type: str  # e.g., "AIRLINE", "HOTEL"


@dataclass
class CardRewardInfo:
    """Additional reward information for a card"""
    card_id: int
    reward_type: RewardType
    point_value: Optional[float] = None  # Value per point in cents
    point_program: Optional[str] = None  # e.g., "Aeroplan", "Scene+"
    transfer_partners: List[TransferPartner] = field(default_factory=list)


@dataclass
class ScrapedCardData:
    """All scraped data for a card"""
    card_id: int
    card_name: str
    bank: str
    usage_tips: List[UsageTip] = field(default_factory=list)
    reward_info: Optional[CardRewardInfo] = None
    scraped_at: str = ""
    source: str = ""

    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.now().isoformat()


# Icon mapping for different tip types and categories
TIP_ICONS = {
    TipType.BEST_USE: {
        "dining": "🍽️",
        "grocery": "🛒",
        "gas": "⛽",
        "travel": "✈️",
        "streaming": "📺",
        "online": "🛍️",
        "default": "💳"
    },
    TipType.REDEMPTION: {
        "points": "🎯",
        "transfer": "🔄",
        "cashback": "💵",
        "default": "💎"
    },
    TipType.STACKING: {
        "default": "📚"
    },
    TipType.AVOID: {
        "default": "⚠️"
    }
}


def get_tip_icon(tip_type: TipType, category: str = "default") -> str:
    """Get appropriate icon for a tip type and category"""
    type_icons = TIP_ICONS.get(tip_type, {})
    return type_icons.get(category.lower(), type_icons.get("default", "💡"))
