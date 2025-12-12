package com.savevia.optimizer.service;

import com.savevia.optimizer.dto.CreditCardDTO;
import com.savevia.optimizer.dto.MissedCashbackSummary;
import com.savevia.optimizer.dto.TransactionDTO;
import com.savevia.optimizer.entity.Transaction;
import com.savevia.optimizer.mapper.TransactionMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.*;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class TransactionAnalysisService {

    private final TransactionMapper transactionMapper;
    private final CardServiceClient cardServiceClient;
    private final TransactionCategorizationService categorizationService;

    /**
     * Analyze transactions and calculate missed cashback
     */
    public void analyzeTransactions(Long userId, List<Long> userCardIds) {
        analyzeTransactions(userId, userCardIds, false);
    }

    /**
     * Analyze transactions with optional force re-analysis
     */
    public void analyzeTransactions(Long userId, List<Long> userCardIds, boolean forceReanalyze) {
        // Get user's cards with reward rules first
        if (userCardIds == null || userCardIds.isEmpty()) {
            log.warn("No card IDs provided for user {}, cannot analyze transactions", userId);
            return;
        }
        var result = cardServiceClient.getCardsByIds(userCardIds);
        List<CreditCardDTO> userCards = result.getData();
        if (userCards == null || userCards.isEmpty()) {
            log.warn("User {} has no cards, cannot analyze transactions", userId);
            return;
        }

        // Reset all transactions if force re-analyze
        if (forceReanalyze) {
            int reset = transactionMapper.resetAnalysisByUserId(userId);
            log.info("Reset {} transactions for user {} for re-analysis", reset, userId);
        }

        List<Transaction> unanalyzed = transactionMapper.findUnanalyzedByUserId(userId);
        if (unanalyzed.isEmpty()) {
            log.info("No unanalyzed transactions for user {}", userId);
            return;
        }

        log.info("Analyzing {} transactions for user {} with {} cards", unanalyzed.size(), userId, userCards.size());

        for (Transaction txn : unanalyzed) {
            analyzeTransaction(txn, userCards);
        }
    }

    /**
     * Analyze a single transaction
     */
    private void analyzeTransaction(Transaction txn, List<CreditCardDTO> userCards) {
        // Ensure category is set
        if (txn.getCategory() == null || txn.getCategory().equals("OTHER")) {
            String category = categorizationService.categorize(txn.getMerchant());
            txn.setCategory(category);
        }

        // Find the best card for this category
        CreditCardDTO bestCard = null;
        BigDecimal bestRate = BigDecimal.ZERO;

        for (CreditCardDTO card : userCards) {
            BigDecimal rate = getRewardRate(card, txn.getCategory());
            if (rate.compareTo(bestRate) > 0) {
                bestRate = rate;
                bestCard = card;
            }
        }

        if (bestCard != null) {
            txn.setBestCardId(bestCard.getId());

            // Calculate optimal cashback
            BigDecimal amount = txn.getAmount().abs();
            BigDecimal optimalCashback = amount.multiply(bestRate).setScale(4, RoundingMode.HALF_UP);
            txn.setOptimalCashback(optimalCashback);

            // Calculate actual cashback (if we know which card was used)
            CreditCardDTO usedCard = null;
            if (txn.getCardUsedId() != null) {
                final Long cardUsedId = txn.getCardUsedId();
                usedCard = userCards.stream()
                        .filter(c -> c.getId().equals(cardUsedId))
                        .findFirst()
                        .orElse(null);
            }

            if (usedCard != null) {
                // Credit card transaction - calculate actual cashback based on the card used
                BigDecimal actualRate = getRewardRate(usedCard, txn.getCategory());
                BigDecimal actualCashback = amount.multiply(actualRate).setScale(4, RoundingMode.HALF_UP);
                txn.setActualCashback(actualCashback);
                txn.setMissedCashback(optimalCashback.subtract(actualCashback).max(BigDecimal.ZERO));
            } else {
                // Debit card / checking / savings account transaction - no cashback earned
                // cardUsedId = null indicates the transaction was made with a debit card or bank transfer
                // This is a missed opportunity - user could have earned cashback with credit card
                txn.setActualCashback(BigDecimal.ZERO);
                txn.setMissedCashback(optimalCashback);
            }
        }

        txn.setIsAnalyzed(true);
        transactionMapper.updateAnalysis(txn);
    }

    /**
     * Get reward rate for a card and category
     */
    private BigDecimal getRewardRate(CreditCardDTO card, String category) {
        if (card.getRewardRules() != null && category != null) {
            for (var rule : card.getRewardRules()) {
                // Compare enum name with category string
                if (rule.getCategory() != null && rule.getCategory().name().equals(category)) {
                    return rule.getRewardRate();
                }
            }
        }
        return card.getBaseRewardRate() != null ? card.getBaseRewardRate() : BigDecimal.ZERO;
    }

    /**
     * Get missed cashback summary for last 90 days
     */
    public MissedCashbackSummary getMissedCashbackSummary(Long userId, List<Long> userCardIds) {
        LocalDateTime startDate = LocalDateTime.now(ZoneOffset.UTC).minusDays(90);
        LocalDateTime endDate = LocalDateTime.now(ZoneOffset.UTC);

        List<Transaction> transactions = transactionMapper.findByUserIdAndDateRange(userId, startDate, endDate);

        // Get user cards if IDs provided
        List<CreditCardDTO> userCards = new ArrayList<>();
        if (userCardIds != null && !userCardIds.isEmpty()) {
            var result = cardServiceClient.getCardsByIds(userCardIds);
            if (result.getData() != null) {
                userCards = result.getData();
            }
        }

        // First analyze any unanalyzed transactions
        List<Transaction> unanalyzed = transactions.stream()
                .filter(t -> !Boolean.TRUE.equals(t.getIsAnalyzed()))
                .collect(Collectors.toList());

        if (!unanalyzed.isEmpty() && !userCards.isEmpty()) {
            for (Transaction txn : unanalyzed) {
                analyzeTransaction(txn, userCards);
            }
            // Refresh from DB
            transactions = transactionMapper.findByUserIdAndDateRange(userId, startDate, endDate);
        }

        // Calculate summary
        MissedCashbackSummary summary = new MissedCashbackSummary();
        summary.setTotalTransactions(transactions.size());

        BigDecimal totalSpending = BigDecimal.ZERO;
        BigDecimal totalActual = BigDecimal.ZERO;
        BigDecimal totalOptimal = BigDecimal.ZERO;
        BigDecimal totalMissed = BigDecimal.ZERO;

        // Debit card statistics
        int debitTxnCount = 0;
        BigDecimal debitSpending = BigDecimal.ZERO;
        BigDecimal debitMissed = BigDecimal.ZERO;

        for (Transaction txn : transactions) {
            if (txn.getCardUsedId() == null) {
                // This is a debit card / checking / savings transaction
                debitTxnCount++;
                debitSpending = debitSpending.add(txn.getAmount().abs());
                if (txn.getMissedCashback() != null) {
                    debitMissed = debitMissed.add(txn.getMissedCashback());
                }
            }
        }

        summary.setDebitTransactions(debitTxnCount);
        summary.setDebitSpending(debitSpending);
        summary.setDebitMissedCashback(debitMissed);

        // Group by category
        Map<String, List<Transaction>> byCategory = transactions.stream()
                .collect(Collectors.groupingBy(t -> t.getCategory() != null ? t.getCategory() : "OTHER"));

        List<MissedCashbackSummary.CategoryMissedCashback> categoryBreakdown = new ArrayList<>();

        for (Map.Entry<String, List<Transaction>> entry : byCategory.entrySet()) {
            String category = entry.getKey();
            List<Transaction> catTxns = entry.getValue();

            BigDecimal catSpending = catTxns.stream()
                    .map(t -> t.getAmount().abs())
                    .reduce(BigDecimal.ZERO, BigDecimal::add);

            BigDecimal catMissed = catTxns.stream()
                    .map(t -> t.getMissedCashback() != null ? t.getMissedCashback() : BigDecimal.ZERO)
                    .reduce(BigDecimal.ZERO, BigDecimal::add);

            totalSpending = totalSpending.add(catSpending);
            totalMissed = totalMissed.add(catMissed);

            // Find best card for this category
            CreditCardDTO bestCard = null;
            BigDecimal bestRate = BigDecimal.ZERO;
            for (CreditCardDTO card : userCards) {
                BigDecimal rate = getRewardRate(card, category);
                if (rate.compareTo(bestRate) > 0) {
                    bestRate = rate;
                    bestCard = card;
                }
            }

            MissedCashbackSummary.CategoryMissedCashback catSummary = new MissedCashbackSummary.CategoryMissedCashback();
            catSummary.setCategory(category);
            catSummary.setSpending(catSpending);
            catSummary.setMissedCashback(catMissed);
            if (bestCard != null) {
                catSummary.setBestCardName(bestCard.getName());
                catSummary.setBestCardBank(bestCard.getBank());
                catSummary.setBestCardRate(bestRate);
            }
            categoryBreakdown.add(catSummary);
        }

        // Sort by spending descending (most spent categories first)
        categoryBreakdown.sort((a, b) -> b.getSpending().compareTo(a.getSpending()));

        // Calculate totals
        for (Transaction txn : transactions) {
            if (txn.getActualCashback() != null) totalActual = totalActual.add(txn.getActualCashback());
            if (txn.getOptimalCashback() != null) totalOptimal = totalOptimal.add(txn.getOptimalCashback());
        }

        summary.setTotalSpending(totalSpending);
        summary.setTotalActualCashback(totalActual);
        summary.setTotalOptimalCashback(totalOptimal);
        summary.setTotalMissedCashback(totalMissed);
        summary.setCategoryBreakdown(categoryBreakdown);

        // Generate top recommendations
        summary.setTopRecommendations(generateRecommendations(categoryBreakdown, userCards));

        return summary;
    }

    /**
     * Get recent transactions with recommendations
     */
    public List<TransactionDTO> getRecentTransactions(Long userId, int limit, List<Long> userCardIds) {
        List<Transaction> transactions = transactionMapper.findRecentByUserId(userId, limit);

        // Get user cards if IDs provided
        List<CreditCardDTO> userCards = new ArrayList<>();
        if (userCardIds != null && !userCardIds.isEmpty()) {
            var result = cardServiceClient.getCardsByIds(userCardIds);
            if (result.getData() != null) {
                userCards = result.getData();
            }
        }

        // Create card lookup map
        Map<Long, CreditCardDTO> cardMap = userCards.stream()
                .collect(Collectors.toMap(CreditCardDTO::getId, c -> c));

        return transactions.stream().map(txn -> {
            TransactionDTO dto = new TransactionDTO();
            dto.setId(txn.getId());
            dto.setUserId(txn.getUserId());
            dto.setAmount(txn.getAmount());
            dto.setMerchant(txn.getMerchant());
            dto.setDescription(txn.getDescription());
            dto.setCategory(txn.getCategory());
            dto.setTransactionDate(txn.getTransactionDate());
            dto.setCardUsedId(txn.getCardUsedId());
            dto.setBestCardId(txn.getBestCardId());
            dto.setActualCashback(txn.getActualCashback());
            dto.setOptimalCashback(txn.getOptimalCashback());
            dto.setMissedCashback(txn.getMissedCashback());
            dto.setIsAnalyzed(txn.getIsAnalyzed());

            // Mark if this is a debit transaction (no credit card used)
            dto.setIsDebitTransaction(txn.getCardUsedId() == null);

            // Add card names
            if (txn.getCardUsedId() != null && cardMap.containsKey(txn.getCardUsedId())) {
                CreditCardDTO usedCard = cardMap.get(txn.getCardUsedId());
                dto.setCardUsedName(usedCard.getBank() + " " + usedCard.getName());
            }
            if (txn.getBestCardId() != null && cardMap.containsKey(txn.getBestCardId())) {
                CreditCardDTO bestCard = cardMap.get(txn.getBestCardId());
                dto.setBestCardName(bestCard.getName());
                dto.setBestCardBank(bestCard.getBank());
                dto.setBestCardRate(getRewardRate(bestCard, txn.getCategory()));
            }

            return dto;
        }).collect(Collectors.toList());
    }

    private List<MissedCashbackSummary.CardRecommendation> generateRecommendations(
            List<MissedCashbackSummary.CategoryMissedCashback> categoryBreakdown,
            List<CreditCardDTO> userCards) {

        // Find which cards would save the most money
        Map<Long, BigDecimal> cardSavings = new HashMap<>();
        Map<Long, List<String>> cardBestCategories = new HashMap<>();

        for (CreditCardDTO card : userCards) {
            BigDecimal savings = BigDecimal.ZERO;
            List<String> bestCats = new ArrayList<>();

            for (var cat : categoryBreakdown) {
                BigDecimal rate = getRewardRate(card, cat.getCategory());
                if (rate.compareTo(BigDecimal.ZERO) > 0 && cat.getMissedCashback().compareTo(BigDecimal.ZERO) > 0) {
                    // This card could have earned something in this category
                    if (cat.getBestCardBank() != null && cat.getBestCardBank().equals(card.getBank())
                            && cat.getBestCardName() != null && cat.getBestCardName().equals(card.getName())) {
                        savings = savings.add(cat.getMissedCashback());
                        bestCats.add(cat.getCategory());
                    }
                }
            }

            cardSavings.put(card.getId(), savings);
            cardBestCategories.put(card.getId(), bestCats);
        }

        // Sort by potential savings
        return userCards.stream()
                .filter(c -> cardSavings.getOrDefault(c.getId(), BigDecimal.ZERO).compareTo(BigDecimal.ZERO) > 0)
                .sorted((a, b) -> cardSavings.get(b.getId()).compareTo(cardSavings.get(a.getId())))
                .limit(3)
                .map(card -> {
                    MissedCashbackSummary.CardRecommendation rec = new MissedCashbackSummary.CardRecommendation();
                    rec.setCardId(card.getId());
                    rec.setCardName(card.getName());
                    rec.setBank(card.getBank());
                    rec.setPotentialSavings(cardSavings.get(card.getId()));
                    rec.setBestCategories(cardBestCategories.get(card.getId()));
                    return rec;
                })
                .collect(Collectors.toList());
    }
}
