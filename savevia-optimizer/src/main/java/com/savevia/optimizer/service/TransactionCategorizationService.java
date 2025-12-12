package com.savevia.optimizer.service;

import com.savevia.optimizer.entity.MerchantCategory;
import com.savevia.optimizer.mapper.MerchantCategoryMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

@Slf4j
@Service
@RequiredArgsConstructor
public class TransactionCategorizationService {

    private final MerchantCategoryMapper merchantCategoryMapper;

    // Cache of merchant patterns (sorted by priority)
    private List<MerchantCategory> merchantPatterns = new CopyOnWriteArrayList<>();

    @PostConstruct
    public void init() {
        refreshPatterns();
    }

    public void refreshPatterns() {
        merchantPatterns = merchantCategoryMapper.findAllActive();
        log.info("Loaded {} merchant category patterns", merchantPatterns.size());
    }

    /**
     * Categorize a transaction based on merchant name
     */
    public String categorize(String merchantName) {
        if (merchantName == null || merchantName.isEmpty()) {
            return "OTHER";
        }

        String upperMerchant = merchantName.toUpperCase();

        // Check patterns in priority order
        for (MerchantCategory pattern : merchantPatterns) {
            if (upperMerchant.contains(pattern.getMerchantPattern().toUpperCase())) {
                return pattern.getCategory();
            }
        }

        return "OTHER";
    }

    /**
     * Categorize with confidence score
     */
    public CategorizationResult categorizeWithConfidence(String merchantName) {
        if (merchantName == null || merchantName.isEmpty()) {
            return new CategorizationResult("OTHER", 0.0);
        }

        String upperMerchant = merchantName.toUpperCase();
        MerchantCategory bestMatch = null;
        int bestPriority = -1;

        for (MerchantCategory pattern : merchantPatterns) {
            if (upperMerchant.contains(pattern.getMerchantPattern().toUpperCase())) {
                if (pattern.getPriority() > bestPriority) {
                    bestMatch = pattern;
                    bestPriority = pattern.getPriority();
                }
            }
        }

        if (bestMatch != null) {
            // Confidence based on priority (0-100 mapped to 0.5-1.0)
            double confidence = 0.5 + (bestPriority / 200.0);
            return new CategorizationResult(bestMatch.getCategory(), Math.min(confidence, 1.0));
        }

        return new CategorizationResult("OTHER", 0.3);
    }

    public static class CategorizationResult {
        public final String category;
        public final double confidence;

        public CategorizationResult(String category, double confidence) {
            this.category = category;
            this.confidence = confidence;
        }
    }
}
