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
public class UserProfileFact {

    private Long id;

    private Long userId;

    private String factCategory;

    private String factKey;

    private String factValue;

    private String source;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
