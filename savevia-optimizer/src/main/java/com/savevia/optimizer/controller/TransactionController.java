package com.savevia.optimizer.controller;

import com.savevia.common.response.Result;
import com.savevia.optimizer.dto.MissedCashbackSummary;
import com.savevia.optimizer.dto.TransactionDTO;
import com.savevia.optimizer.service.TransactionAnalysisService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@RestController
@RequestMapping("/api/v1/optimize/transactions")
@RequiredArgsConstructor
public class TransactionController {

    private final TransactionAnalysisService transactionAnalysisService;

    /**
     * Parse comma-separated card IDs from header
     */
    private List<Long> parseCardIds(String cardIdsHeader) {
        if (cardIdsHeader == null || cardIdsHeader.trim().isEmpty()) {
            return new ArrayList<>();
        }
        try {
            return Arrays.stream(cardIdsHeader.split(","))
                    .map(String::trim)
                    .filter(s -> !s.isEmpty())
                    .map(Long::parseLong)
                    .collect(Collectors.toList());
        } catch (NumberFormatException e) {
            log.warn("Failed to parse card IDs: {}", cardIdsHeader);
            return new ArrayList<>();
        }
    }

    /**
     * Get recent transactions with recommendations
     */
    @GetMapping
    public Result<List<TransactionDTO>> getRecentTransactions(
            @RequestHeader("X-User-Id") Long userId,
            @RequestHeader(value = "X-User-Card-Ids", required = false) String cardIdsHeader,
            @RequestParam(defaultValue = "50") int limit) {

        List<Long> cardIds = parseCardIds(cardIdsHeader);
        log.info("Getting {} recent transactions for user {} with {} cards", limit, userId, cardIds.size());

        List<TransactionDTO> transactions = transactionAnalysisService.getRecentTransactions(userId, limit, cardIds);
        return Result.success(transactions);
    }

    /**
     * Get missed cashback summary for last 90 days
     */
    @GetMapping("/summary")
    public Result<MissedCashbackSummary> getMissedCashbackSummary(
            @RequestHeader("X-User-Id") Long userId,
            @RequestHeader(value = "X-User-Card-Ids", required = false) String cardIdsHeader) {

        List<Long> cardIds = parseCardIds(cardIdsHeader);
        log.info("Getting missed cashback summary for user {} with {} cards", userId, cardIds.size());

        MissedCashbackSummary summary = transactionAnalysisService.getMissedCashbackSummary(userId, cardIds);
        return Result.success(summary);
    }

    /**
     * Trigger analysis of unanalyzed transactions
     */
    @PostMapping("/analyze")
    public Result<Void> analyzeTransactions(
            @RequestHeader("X-User-Id") Long userId,
            @RequestHeader(value = "X-User-Card-Ids", required = false) String cardIdsHeader,
            @RequestParam(defaultValue = "false") boolean force) {

        List<Long> cardIds = parseCardIds(cardIdsHeader);
        log.info("Analyzing transactions for user {} with {} cards, force={}", userId, cardIds.size(), force);

        transactionAnalysisService.analyzeTransactions(userId, cardIds, force);
        return Result.success(null);
    }
}
