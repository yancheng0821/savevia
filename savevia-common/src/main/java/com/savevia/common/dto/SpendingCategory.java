package com.savevia.common.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public enum SpendingCategory {

    // Core categories
    DINING("Dining", "餐饮"),
    GROCERY("Grocery", "超市"),
    GAS("Gas", "加油"),
    TRAVEL("Travel", "旅行"),
    STREAMING("Streaming", "流媒体订阅"),
    TRANSIT("Transit", "公共交通"),
    PHARMACY("Pharmacy", "药房"),
    RENT("Rent", "房租"),
    RECURRING("Recurring Bills", "固定账单"),
    ONLINE_SHOPPING("Online Shopping", "网购"),
    FOREIGN("Foreign Currency", "外币消费"),

    // Extended categories
    RETAIL("Retail", "零售购物"),
    ENTERTAINMENT("Entertainment", "娱乐"),
    PERSONAL_SERVICES("Personal Services", "个人服务"),
    HOME_IMPROVEMENT("Home Improvement", "家装建材"),
    WHOLESALE("Wholesale", "仓储会员店"),
    INSURANCE("Insurance", "保险"),
    TELECOM("Telecom", "电信"),
    EV_CHARGING("EV Charging", "电动车充电"),

    // Catch-all
    OTHER("Other", "其他");

    private final String displayName;
    private final String displayNameZh;
}
