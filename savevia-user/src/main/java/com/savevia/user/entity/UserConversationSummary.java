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
public class UserConversationSummary {

    private Long id;

    private Long userId;

    private String summary;

    private String keyTopics;

    private String recommendations;

    private String sourceConversationIds;

    private LocalDateTime createdAt;
}
