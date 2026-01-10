package com.savevia.user.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserInsight {
    private Long id;
    private Long userId;
    private String insightType;     // 'spending_pattern', 'upcoming_event', 'preference'
    private String insightKey;      // 'grocery_day', 'travel_plan', 'favorite_category'
    private String insightValue;    // JSON string
    private BigDecimal confidence;  // 0.00-1.00
    private String source;          // 'chat', 'transaction', 'behavior'
    private LocalDateTime expiresAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
