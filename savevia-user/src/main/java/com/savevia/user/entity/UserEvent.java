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
public class UserEvent {
    private Long id;
    private String eventType;
    private Long userId;
    private String sessionId;
    private LocalDateTime createdAt;
}
