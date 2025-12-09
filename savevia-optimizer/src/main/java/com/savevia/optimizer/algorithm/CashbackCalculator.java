package com.savevia.optimizer.algorithm;

import com.savevia.common.dto.SpendingCategory;
import com.savevia.optimizer.dto.CreditCardDTO;
import com.savevia.optimizer.dto.RewardRuleDTO;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.math.RoundingMode;

@Component
public class CashbackCalculator {

    /**
     * Calculate reward for a specific spending category with a given card
     */
    public BigDecimal calculateReward(CreditCardDTO card, SpendingCategory category, BigDecimal amount) {
        BigDecimal rate = getRewardRate(card, category);
        BigDecimal reward = amount.multiply(rate).setScale(2, RoundingMode.HALF_UP);

        // Apply monthly cap if exists
        BigDecimal cap = getMonthlyCap(card, category);
        if (cap != null && cap.compareTo(BigDecimal.ZERO) > 0) {
            BigDecimal maxReward = cap.multiply(rate);
            if (reward.compareTo(maxReward) > 0) {
                reward = maxReward;
            }
        }

        return reward;
    }

    /**
     * Get reward rate for a specific category
     */
    public BigDecimal getRewardRate(CreditCardDTO card, SpendingCategory category) {
        if (card.getRewardRules() == null || card.getRewardRules().isEmpty()) {
            return card.getBaseRewardRate() != null ? card.getBaseRewardRate() : new BigDecimal("0.01");
        }

        BigDecimal defaultRate = card.getBaseRewardRate() != null ? card.getBaseRewardRate() : new BigDecimal("0.01");

        return card.getRewardRules().stream()
            .filter(rule -> rule.getCategory() == category)
            .map(RewardRuleDTO::getRewardRate)
            .filter(rate -> rate != null)
            .findFirst()
            .orElse(defaultRate);
    }

    /**
     * Get monthly cap for a specific category
     */
    public BigDecimal getMonthlyCap(CreditCardDTO card, SpendingCategory category) {
        if (card.getRewardRules() == null) {
            return null;
        }

        return card.getRewardRules().stream()
            .filter(rule -> rule.getCategory() == category)
            .map(RewardRuleDTO::getMonthlyCapAmount)
            .filter(cap -> cap != null)
            .findFirst()
            .orElse(null);
    }

    /**
     * Format reward rate as percentage string
     */
    public String formatRateAsPercentage(BigDecimal rate) {
        return rate.multiply(BigDecimal.valueOf(100))
            .setScale(1, RoundingMode.HALF_UP)
            .stripTrailingZeros()
            .toPlainString() + "%";
    }
}
