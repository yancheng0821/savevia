package com.savevia.common.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public enum SpendingCategory {

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
    OTHER("Other", "其他");

    private final String displayName;
    private final String displayNameZh;
}
