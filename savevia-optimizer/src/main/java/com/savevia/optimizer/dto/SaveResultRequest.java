package com.savevia.optimizer.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class SaveResultRequest {
    @NotNull(message = "Result is required")
    private OptimizationResult result;
}
