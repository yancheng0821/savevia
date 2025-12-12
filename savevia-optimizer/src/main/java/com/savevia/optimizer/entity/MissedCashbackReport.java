package com.savevia.optimizer.entity;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
public class MissedCashbackReport {
    private Long id;
    private Long userId;
    private String reportType; // 90days, monthly, yearly
    private LocalDate startDate;
    private LocalDate endDate;
    private Integer totalTransactions;
    private BigDecimal totalSpending;
    private BigDecimal totalActualCashback;
    private BigDecimal totalOptimalCashback;
    private BigDecimal totalMissedCashback;
    private String categoryBreakdown; // JSON
    private String topRecommendations; // JSON
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
