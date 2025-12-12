package com.savevia.user.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class UpdateSubscriptionRequest {

    @NotBlank(message = "Subscription type is required")
    private String subscriptionType;  // FREE or PRO

    private String expiresAt;  // ISO 8601 format, e.g., "2025-12-31T23:59:59Z"

    @NotBlank(message = "Platform is required")
    private String platform;  // ios, android, web

    private String productId;  // Product ID from App Store / Google Play
}
