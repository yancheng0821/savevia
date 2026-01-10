package com.savevia.user.entity;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class AiUsage {
    private Long id;
    private Long userId;
    private String yearMonth;
    private Integer usageCount;        // Card recommendation usage
    private Integer monthlyLimit;       // Card recommendation limit
    private Integer chatUsageCount;     // Chat usage
    private Integer chatMonthlyLimit;   // Chat limit
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
