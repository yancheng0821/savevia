package com.savevia.card.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SignupBonusDTO {

    private BigDecimal bonusAmount;
    private BigDecimal minSpend;
    private Integer daysToComplete;
    private String description;                    // 英文描述（旧前端兼容）
    private Map<String, String> descriptionI18n;   // 多语言描述（新前端用）
}
