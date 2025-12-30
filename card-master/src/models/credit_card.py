"""
Credit Card data models - Pydantic schemas for credit card information.
Reference: savevia.app API structure
"""

from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SpendingCategory(str, Enum):
    """Spending category enum - matches savevia.app categories"""
    DINING = "DINING"
    GROCERY = "GROCERY"
    GAS = "GAS"
    TRAVEL = "TRAVEL"
    TRANSIT = "TRANSIT"
    STREAMING = "STREAMING"
    ENTERTAINMENT = "ENTERTAINMENT"
    PERSONAL_SERVICES = "PERSONAL_SERVICES"
    RETAIL = "RETAIL"
    HOME_IMPROVEMENT = "HOME_IMPROVEMENT"
    RECURRING = "RECURRING"
    PHARMACY = "PHARMACY"
    FOREIGN = "FOREIGN"
    ONLINE_SHOPPING = "ONLINE_SHOPPING"
    EV_CHARGING = "EV_CHARGING"
    TELECOM = "TELECOM"
    INSURANCE = "INSURANCE"
    RENT = "RENT"
    WHOLESALE = "WHOLESALE"
    OTHER = "OTHER"


# Category Chinese names mapping
CATEGORY_CN_NAMES: dict[str, str] = {
    "DINING": "餐饮",
    "GROCERY": "超市",
    "GAS": "加油",
    "TRAVEL": "旅行",
    "TRANSIT": "公交",
    "STREAMING": "流媒体",
    "ENTERTAINMENT": "娱乐",
    "PERSONAL_SERVICES": "个人服务",
    "RETAIL": "零售购物",
    "HOME_IMPROVEMENT": "家装建材",
    "RECURRING": "定期账单",
    "PHARMACY": "药店",
    "FOREIGN": "境外消费",
    "ONLINE_SHOPPING": "网购",
    "EV_CHARGING": "电车充电",
    "TELECOM": "通讯",
    "INSURANCE": "保险",
    "RENT": "房租",
    "WHOLESALE": "批发",
    "OTHER": "其他",
}

# Category icons (emoji)
CATEGORY_ICONS: dict[str, str] = {
    "DINING": "🍽️",
    "GROCERY": "🛒",
    "GAS": "⛽",
    "TRAVEL": "✈️",
    "TRANSIT": "🚌",
    "STREAMING": "📺",
    "ENTERTAINMENT": "🎬",
    "PERSONAL_SERVICES": "💅",
    "RETAIL": "🛍️",
    "HOME_IMPROVEMENT": "🔧",
    "RECURRING": "📋",
    "PHARMACY": "💊",
    "FOREIGN": "🌍",
    "ONLINE_SHOPPING": "🛒",
    "EV_CHARGING": "🔌",
    "TELECOM": "📱",
    "INSURANCE": "🛡️",
    "RENT": "🏠",
    "WHOLESALE": "📦",
    "OTHER": "📌",
}


class CardType(str, Enum):
    """Credit card network type"""
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    AMEX = "AMEX"


class SignupBonus(BaseModel):
    """Signup bonus information"""
    bonus_amount: int = Field(default=0, description="Bonus amount (points or dollars)")
    min_spend: int = Field(default=0, description="Minimum spend required")
    days_to_complete: int = Field(default=0, description="Days to complete the spend")
    description: Optional[str] = Field(default=None, description="Bonus description")

    class Config:
        # Allow snake_case in Python but accept camelCase from JSON
        populate_by_name = True

    @classmethod
    def from_api(cls, data: dict) -> "SignupBonus":
        """Create from savevia.app API response format (camelCase)"""
        if data is None:
            return cls()
        return cls(
            bonus_amount=data.get("bonusAmount", 0),
            min_spend=data.get("minSpend", 0),
            days_to_complete=data.get("daysToComplete", 0),
            description=data.get("description"),
        )


class RewardRule(BaseModel):
    """Reward rule for a specific spending category"""
    id: Optional[int] = Field(default=None, description="Rule ID")
    category: str = Field(..., description="Spending category")
    reward_rate: Decimal = Field(..., description="Reward rate (e.g., 0.05 = 5%)")
    monthly_cap_amount: Optional[Decimal] = Field(
        default=None, description="Monthly spending cap"
    )
    description: Optional[str] = Field(default=None, description="Rule description")

    class Config:
        populate_by_name = True

    @classmethod
    def from_api(cls, data: dict) -> "RewardRule":
        """Create from savevia.app API response format (camelCase)"""
        return cls(
            id=data.get("id"),
            category=data.get("category", "OTHER"),
            reward_rate=Decimal(str(data.get("rewardRate", 0))),
            monthly_cap_amount=(
                Decimal(str(data["monthlyCapAmount"]))
                if data.get("monthlyCapAmount")
                else None
            ),
            description=data.get("description"),
        )

    @property
    def reward_rate_percent(self) -> str:
        """Return reward rate as percentage string (e.g., '5%')"""
        return f"{float(self.reward_rate) * 100:.0f}%"

    @property
    def category_cn(self) -> str:
        """Return Chinese category name"""
        return CATEGORY_CN_NAMES.get(self.category, self.category)

    @property
    def category_icon(self) -> str:
        """Return category icon emoji"""
        return CATEGORY_ICONS.get(self.category, "📌")


class CreditCard(BaseModel):
    """Credit card information model"""
    id: int = Field(..., description="Card ID")
    bank: str = Field(..., description="Bank name")
    name: str = Field(..., description="Card name")
    card_type: str = Field(..., description="Card network (VISA/MASTERCARD/AMEX)")
    annual_fee: Decimal = Field(default=Decimal("0"), description="Annual fee")
    base_reward_rate: Decimal = Field(
        default=Decimal("0.01"), description="Base reward rate"
    )
    image_url: Optional[str] = Field(
        default=None, description="Card image URL or gradient style"
    )
    apply_url: Optional[str] = Field(default=None, description="Application URL")
    no_fx_fee: bool = Field(default=False, description="No foreign transaction fee")
    signup_bonus: Optional[SignupBonus] = Field(
        default=None, description="Signup bonus info"
    )
    reward_rules: list[RewardRule] = Field(
        default_factory=list, description="Reward rules by category"
    )

    class Config:
        populate_by_name = True

    @classmethod
    def from_api(cls, data: dict) -> "CreditCard":
        """Create from savevia.app API response format (camelCase)"""
        signup_bonus = None
        if data.get("signupBonus"):
            signup_bonus = SignupBonus.from_api(data["signupBonus"])

        reward_rules = [
            RewardRule.from_api(rule) for rule in data.get("rewardRules", [])
        ]

        return cls(
            id=data["id"],
            bank=data["bank"],
            name=data["name"],
            card_type=data.get("cardType", "VISA"),
            annual_fee=Decimal(str(data.get("annualFee", 0))),
            base_reward_rate=Decimal(str(data.get("baseRewardRate", 0.01))),
            image_url=data.get("imageUrl"),
            apply_url=data.get("applyUrl"),
            no_fx_fee=data.get("noFxFee", False),
            signup_bonus=signup_bonus,
            reward_rules=reward_rules,
        )

    @property
    def base_reward_rate_percent(self) -> str:
        """Return base reward rate as percentage string"""
        return f"{float(self.base_reward_rate) * 100:.1f}%"

    def get_reward_rate_for_category(self, category: str) -> Decimal:
        """Get the reward rate for a specific category"""
        for rule in self.reward_rules:
            if rule.category == category:
                return rule.reward_rate
        return self.base_reward_rate

    def get_rule_for_category(self, category: str) -> Optional[RewardRule]:
        """Get the reward rule for a specific category"""
        for rule in self.reward_rules:
            if rule.category == category:
                return rule
        return None


class CardRankItem(BaseModel):
    """Card ranking item for a specific category"""
    card: CreditCard
    category: str
    reward_rate: Decimal
    reward_rate_percent: str
    monthly_cap: Optional[Decimal] = None
    description: Optional[str] = None

    @property
    def category_cn(self) -> str:
        return CATEGORY_CN_NAMES.get(self.category, self.category)
