package com.savevia.optimizer.dto;

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
public class CategoryRecommendation {

    private SpendingCategory category;
    private BigDecimal monthlySpend;
    private CreditCardDTO recommendedCard;
    private BigDecimal rewardRate;
    private BigDecimal monthlyReward;
    private String explanation;
}
