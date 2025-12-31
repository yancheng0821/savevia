package com.savevia.user.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class AdminUserDTO {
    private Long id;
    private String name;
    private String email;
    private String createdAt; // ISO date

    // Subscription info
    private String subscriptionType;      // FREE or PRO
    private String subscriptionPlatform;  // ios, android, web
    private String subscriptionProductId;
    private String subscriptionExpiresAt; // ISO date

    // Activity info
    private boolean active; // Has events in last 7 days
}
