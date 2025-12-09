package com.savevia.optimizer.dto;

import com.savevia.common.dto.SpendingCategory;
import jakarta.validation.constraints.NotEmpty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OptimizationRequest {

    @NotEmpty(message = "At least one card must be selected")
    private List<Long> cardIds;

    @NotEmpty(message = "Spending data is required")
    private Map<SpendingCategory, BigDecimal> monthlySpending;
}
