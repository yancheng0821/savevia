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
public class CreditCard {

    private Long id;

    private String bank;

    private String name;

    private String cardType;

    private BigDecimal annualFee;

    private BigDecimal baseRewardRate;

    private String signupBonusJson;

    private String imageUrl;

    private String applyUrl;

    private Boolean noFxFee;

    private String rewardType;

    private BigDecimal pointValue;

    private String pointProgram;

    private String transferPartnersJson;

    private BigDecimal amexTravelBonusRate;

    private Boolean isActive;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;
}
