package com.savevia.optimizer.dto;

import lombok.Data;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@Data
public class MissedCashbackSummary {
    private Integer totalTransactions;
    private BigDecimal totalSpending;
    private BigDecimal totalActualCashback;
    private BigDecimal totalOptimalCashback;
    private BigDecimal totalMissedCashback;

    // Debit card analysis (transactions without credit card)
    private Integer debitTransactions;      // Count of debit/checking transactions
    private BigDecimal debitSpending;       // Total spending via debit cards
    private BigDecimal debitMissedCashback; // Cashback lost by not using credit cards

    // Per category breakdown
    private List<CategoryMissedCashback> categoryBreakdown;

    // Top recommendations
    private List<CardRecommendation> topRecommendations;

    @Data
    public static class CategoryMissedCashback {
        private String category;
        private BigDecimal spending;
        private BigDecimal missedCashback;
        private String bestCardName;
        private String bestCardBank;
        private BigDecimal bestCardRate;
    }

    @Data
    public static class CardRecommendation {
        private Long cardId;
        private String cardName;
        private String bank;
        private BigDecimal potentialSavings;
        private List<String> bestCategories;
    }
}
