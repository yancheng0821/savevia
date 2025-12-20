package com.savevia.card.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AffiliateLink {

    private Long id;

    private Long cardId;

    private String bankName;

    private String affiliateType;

    private String affiliateUrl;

    private BigDecimal commissionAmount;

    private Boolean isActive;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
