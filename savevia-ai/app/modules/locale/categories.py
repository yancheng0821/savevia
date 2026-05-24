"""SpendingCategory enum — mirrors com.savevia.common.dto.SpendingCategory.

Names and display strings MUST stay synchronised with the Java enum so that
LLM-generated tool arguments (which the LLM picks from the schema enum list)
deserialise without translation. If Java adds a new category, add it here too.
"""

from __future__ import annotations

from enum import Enum


class SpendingCategory(Enum):
    # (Java name, English display, Chinese display)
    DINING = ("Dining", "餐饮")
    GROCERY = ("Grocery", "超市")
    GAS = ("Gas", "加油")
    TRAVEL = ("Travel", "旅行")
    STREAMING = ("Streaming", "流媒体订阅")
    TRANSIT = ("Transit", "公共交通")
    PHARMACY = ("Pharmacy", "药房")
    RENT = ("Rent", "房租")
    RECURRING = ("Recurring Bills", "固定账单")
    ONLINE_SHOPPING = ("Online Shopping", "网购")
    FOREIGN = ("Foreign Currency", "外币消费")
    RETAIL = ("Retail", "零售购物")
    ENTERTAINMENT = ("Entertainment", "娱乐")
    PERSONAL_SERVICES = ("Personal Services", "个人服务")
    HOME_IMPROVEMENT = ("Home Improvement", "家装建材")
    WHOLESALE = ("Wholesale", "仓储会员店")
    INSURANCE = ("Insurance", "保险")
    TELECOM = ("Telecom", "电信")
    EV_CHARGING = ("EV Charging", "电动车充电")
    LIQUOR = ("Liquor", "酒类")
    OTHER = ("Other", "其他")

    def __init__(self, display_name: str, display_name_zh: str):
        self.display_name = display_name
        self.display_name_zh = display_name_zh

    @classmethod
    def from_str(cls, value: str | None) -> "SpendingCategory | None":
        """Case-insensitive lookup by name; returns None for unknown / empty."""
        if not value:
            return None
        try:
            return cls[value.upper()]
        except KeyError:
            return None

    @classmethod
    def names(cls) -> list[str]:
        """Tool-schema-friendly list of enum names, in declaration order."""
        return [c.name for c in cls]
