package com.savevia.optimizer.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OptimizationResult {

    private List<CategoryRecommendation> recommendations;
    private BigDecimal monthlyReward;
    private BigDecimal annualReward;
    private BigDecimal totalAnnualFees;
    private BigDecimal netAnnualSavings;
    private String summary;
}
