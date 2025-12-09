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
public class RewardRuleDTO {

    private Long id;
    private SpendingCategory category;
    private BigDecimal rewardRate;
    private BigDecimal monthlyCapAmount;
    private String description;
}
