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
public class PushNotification {
    private Long id;
    private Long userId;
    private String notificationType;    // 'spending_reminder', 'travel_alert', 'promo_expiry', 'missed_reward'
    private String title;
    private String body;
    private String data;                // JSON string
    private String locale;
    private LocalDateTime scheduledAt;
    private LocalDateTime sentAt;
    private LocalDateTime readAt;
    private String status;              // 'pending', 'sent', 'failed', 'cancelled', 'read'
    private String errorMessage;
    private LocalDateTime createdAt;
}
