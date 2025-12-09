package com.savevia.card.entity;

import com.savevia.common.dto.SpendingCategory;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RewardRule {

    private Long id;

    private Long cardId;

    private String category;

    private BigDecimal rewardRate;

    private BigDecimal monthlyCapAmount;

    private String mccCodes;

    private String description;

    public SpendingCategory getCategoryEnum() {
        try {
            return SpendingCategory.valueOf(this.category);
        } catch (Exception e) {
            return SpendingCategory.OTHER;
        }
    }
}
