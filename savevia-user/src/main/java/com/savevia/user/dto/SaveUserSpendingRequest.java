package com.savevia.user.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;
import java.math.BigDecimal;
import java.util.Map;

@Data
public class SaveUserSpendingRequest {
    @NotNull(message = "Spending data is required")
    private Map<String, BigDecimal> spending;
}
