package com.savevia.optimizer.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
public class SavedResult {
    private Long id;
    private String shareId;  // Unique shareable ID (e.g., "abc123")
    private Long userId;     // Optional - null for anonymous shares
    private String resultJson;  // Full result as JSON
    private BigDecimal netAnnualSavings;
    private BigDecimal annualReward;
    private BigDecimal totalAnnualFees;
    private LocalDateTime createdAt;
    private LocalDateTime expiresAt;  // Optional expiry for shared links
}
