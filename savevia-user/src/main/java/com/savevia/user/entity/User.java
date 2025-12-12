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
public class User {

    private Long id;

    private String email;

    private String passwordHash;

    private String name;

    private String googleId;

    private String appleId;

    private String avatarUrl;

    private Boolean isActive;

    private Boolean emailVerified;

    private String emailVerificationToken;

    private LocalDateTime emailVerificationExpiresAt;

    private String passwordResetToken;

    private LocalDateTime passwordResetExpiresAt;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    // Subscription fields
    private String subscriptionType;  // FREE or PRO

    private LocalDateTime subscriptionExpiresAt;

    private String subscriptionPlatform;  // ios, android, web

    private String subscriptionProductId;
}
