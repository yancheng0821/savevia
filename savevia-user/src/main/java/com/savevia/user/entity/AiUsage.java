package com.savevia.user.entity;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class AiUsage {
    private Long id;
    private Long userId;
    private String yearMonth;
    private Integer usageCount;
    private Integer monthlyLimit;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
