package com.savevia.optimizer.entity;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class MerchantCategory {
    private Long id;
    private String merchantPattern;
    private String category;
    private Integer priority;
    private Boolean isActive;
    private LocalDateTime createdAt;
}
