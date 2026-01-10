package com.savevia.card.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CreditCardDTO {

    private Long id;
    private String bank;
    private String name;
    private String cardType;
    private BigDecimal annualFee;
    private BigDecimal baseRewardRate;
    private String rewardType;  // CASHBACK or POINTS
    private String pointProgram;  // e.g., "AIR MILES", "Aeroplan", "MR Points"
    private BigDecimal pointValue;  // Value per point in dollars (e.g., 0.018 = 1.8¢/point)
    private String imageUrl;
    private String applyUrl;
    private Boolean noFxFee;
    private SignupBonusDTO signupBonus;
    private List<RewardRuleDTO> rewardRules;

    // Amex Travel Online 额外积分倍率
    private BigDecimal amexTravelBonusRate;

    // 联盟链接信息
    private AffiliateLinkDTO affiliateLink;
}
