package com.savevia.user.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MemoryExtractionLog {

    private Long id;

    private Long conversationId;

    private Long userId;

    private String status;

    private LocalDateTime processedAt;

    private String errorMessage;

    private LocalDateTime createdAt;
}
