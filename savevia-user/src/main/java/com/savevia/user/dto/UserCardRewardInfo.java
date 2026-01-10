package com.savevia.user.dto;

import lombok.Data;
import java.math.BigDecimal;

/**
 * User's card reward information for smart push notifications
 */
@Data
public class UserCardRewardInfo {
    private Long cardId;
    private String cardName;        // "TD Cash Back Visa Infinite"
    private String bank;            // "TD"
    private String cardType;        // "cashback" / "points" / "travel"
    private String category;        // "grocery", "dining", "gas", etc.
    private BigDecimal rewardRate;  // 0.03 means 3% or 3x points
    private BigDecimal monthlyCap;  // Monthly reward cap amount
    private String rewardUnit;      // "%" for cashback, "x" for points

    /**
     * Get formatted reward rate string (e.g., "3%" or "5x")
     */
    public String getFormattedRewardRate() {
        if (rewardRate == null) return "";
        int rate = rewardRate.multiply(BigDecimal.valueOf(100)).intValue();
        return rate + rewardUnit;
    }

    /**
     * Check if this is a cashback card
     */
    public boolean isCashbackCard() {
        return "cashback".equalsIgnoreCase(cardType) || "%".equals(rewardUnit);
    }

    /**
     * Check if this is a points card
     */
    public boolean isPointsCard() {
        return "points".equalsIgnoreCase(cardType) || "x".equals(rewardUnit);
    }
}
