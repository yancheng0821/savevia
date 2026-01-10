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
public class UserDevice {
    private Long id;
    private Long userId;
    private String deviceToken;
    private String platform;        // 'ios', 'android', 'web'
    private String deviceName;
    private String appVersion;
    private String osVersion;
    private String locale;          // 'en', 'zh', 'fr', 'ja', 'ko', 'es'
    private Boolean isActive;
    private LocalDateTime lastUsedAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
