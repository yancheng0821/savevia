package com.savevia.card.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CardUsageTip {

    private Long id;

    private Long cardId;

    private String tipType;

    private String titleJson;

    private String contentJson;

    private String icon;

    private Integer priority;

    private Boolean isActive;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
