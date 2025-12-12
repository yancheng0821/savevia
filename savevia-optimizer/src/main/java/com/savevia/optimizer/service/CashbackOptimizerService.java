package com.savevia.optimizer.service;

import com.savevia.common.dto.SpendingCategory;
import com.savevia.common.exception.BusinessException;
import com.savevia.common.exception.ErrorCode;
import com.savevia.common.response.Result;
import com.savevia.optimizer.algorithm.CashbackCalculator;
import com.savevia.optimizer.dto.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class CashbackOptimizerService {

    private final CardServiceClient cardClient;
    private final UserServiceClient userClient;
    private final CashbackCalculator calculator;
    private final OpenAiService openAiService;

    /**
     * Main optimization method - finds the best card for each spending category
     */
    public OptimizationResult optimize(OptimizationRequest request) {
        // Validate request
        if (request.getCardIds() == null || request.getCardIds().isEmpty()) {
            throw new BusinessException(ErrorCode.NO_CARDS_SELECTED);
        }
        if (request.getMonthlySpending() == null || request.getMonthlySpending().isEmpty()) {
            throw new BusinessException(ErrorCode.INVALID_SPENDING_DATA);
        }

        // Fetch card details from Card Service
        Result<List<CreditCardDTO>> cardResult = cardClient.getCardsByIds(request.getCardIds());
        if (!cardResult.isSuccess() || cardResult.getData() == null || cardResult.getData().isEmpty()) {
            throw new BusinessException(ErrorCode.CARD_NOT_FOUND, "Failed to fetch card details");
        }

        List<CreditCardDTO> userCards = cardResult.getData();
        Map<SpendingCategory, BigDecimal> spending = request.getMonthlySpending();

        // Calculate optimal card for each category
        List<CategoryRecommendation> recommendations = new ArrayList<>();
        BigDecimal totalMonthlyReward = BigDecimal.ZERO;

        for (Map.Entry<SpendingCategory, BigDecimal> entry : spending.entrySet()) {
            SpendingCategory category = entry.getKey();
            BigDecimal amount = entry.getValue();

            if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
                continue;
            }

            CreditCardDTO bestCard = null;
            BigDecimal bestReward = BigDecimal.ZERO;
            BigDecimal bestRate = BigDecimal.ZERO;

            for (CreditCardDTO card : userCards) {
                BigDecimal reward = calculator.calculateReward(card, category, amount);
                if (reward.compareTo(bestReward) > 0) {
                    bestReward = reward;
                    bestCard = card;
                    bestRate = calculator.getRewardRate(card, category);
                }
            }

            if (bestCard != null) {
                String explanation = String.format(
                    "Use %s %s for %s - earn %s cashback (%s)",
                    bestCard.getBank(),
                    bestCard.getName(),
                    category.getDisplayName(),
                    formatCurrency(bestReward),
                    calculator.formatRateAsPercentage(bestRate)
                );

                recommendations.add(CategoryRecommendation.builder()
                    .category(category)
                    .monthlySpend(amount)
                    .recommendedCard(bestCard)
                    .rewardRate(bestRate)
                    .monthlyReward(bestReward)
                    .explanation(explanation)
                    .build());

                totalMonthlyReward = totalMonthlyReward.add(bestReward);
            }
        }

        // Calculate annual figures
        BigDecimal annualReward = totalMonthlyReward.multiply(BigDecimal.valueOf(12));
        BigDecimal totalAnnualFees = userCards.stream()
            .map(card -> card.getAnnualFee() != null ? card.getAnnualFee() : BigDecimal.ZERO)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
        BigDecimal netAnnualSavings = annualReward.subtract(totalAnnualFees);

        // Generate summary
        String summary = String.format(
            "With your current cards, you can earn %s per year in cashback. " +
            "After deducting %s in annual fees, your net savings would be %s.",
            formatCurrency(annualReward),
            formatCurrency(totalAnnualFees),
            formatCurrency(netAnnualSavings)
        );

        // Generate AI explanations if enabled, user is logged in, and has quota
        if (Boolean.TRUE.equals(request.getEnableAiExplanation()) && request.getUserId() != null) {
            try {
                // Check if user can use AI
                Result<Boolean> canUseResult = userClient.checkCanUseAi(request.getUserId());
                if (canUseResult.isSuccess() && Boolean.TRUE.equals(canUseResult.getData())) {
                    openAiService.generateExplanations(recommendations, userCards, request.getLocale());
                    // Record usage after successful AI generation
                    userClient.recordAiUsage(request.getUserId());
                } else {
                    log.info("User {} has reached AI usage limit", request.getUserId());
                }
            } catch (Exception e) {
                log.warn("Failed to generate AI explanations: {}", e.getMessage());
            }
        } else if (Boolean.TRUE.equals(request.getEnableAiExplanation()) && request.getUserId() == null) {
            // Guest user - AI disabled, must login to use AI feature
            log.info("Guest user attempted to use AI feature - login required");
        }

        return OptimizationResult.builder()
            .recommendations(recommendations)
            .monthlyReward(totalMonthlyReward.setScale(2, RoundingMode.HALF_UP))
            .annualReward(annualReward.setScale(2, RoundingMode.HALF_UP))
            .totalAnnualFees(totalAnnualFees.setScale(2, RoundingMode.HALF_UP))
            .netAnnualSavings(netAnnualSavings.setScale(2, RoundingMode.HALF_UP))
            .summary(summary)
            .build();
    }

    private String formatCurrency(BigDecimal amount) {
        return "$" + amount.setScale(2, RoundingMode.HALF_UP).toPlainString();
    }
}
