package com.savevia.optimizer.entity;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class BankConnection {
    private Long id;
    private Long userId;
    private String flinksLoginId;
    private String institutionName;
    private String status; // PENDING, CONNECTED, REFRESHING, ERROR, DISCONNECTED
    private LocalDateTime lastSyncAt;
    private String errorMessage;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
