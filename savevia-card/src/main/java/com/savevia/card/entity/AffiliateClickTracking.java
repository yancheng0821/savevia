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
public class AffiliateClickTracking {

    private Long id;

    private Long userId;

    private Long cardId;

    private Long affiliateLinkId;

    private String bankName;

    private LocalDateTime clickedAt;
}
