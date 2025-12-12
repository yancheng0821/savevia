package com.savevia.optimizer.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.savevia.common.dto.SpendingCategory;
import com.savevia.optimizer.dto.CategoryRecommendation;
import com.savevia.optimizer.dto.CreditCardDTO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

@Slf4j
@Service
public class OpenAiService {

    @Value("${openai.api.key:}")
    private String apiKey;

    @Value("${openai.api.model:gpt-4o-mini}")
    private String model;

    @Value("${openai.api.base-url:https://api.openai.com}")
    private String baseUrl;

    @Value("${openai.enabled:true}")
    private boolean enabled;

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    private final ExecutorService executor = Executors.newFixedThreadPool(6);

    public OpenAiService(RestTemplate restTemplate, ObjectMapper objectMapper) {
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
    }

    /**
     * Generate AI explanations for all recommendations using parallel API calls
     */
    public void generateExplanations(List<CategoryRecommendation> recommendations,
                                     List<CreditCardDTO> userCards,
                                     String locale) {
        if (!enabled || apiKey == null || apiKey.isEmpty()) {
            log.info("OpenAI is disabled or API key not configured");
            return;
        }

        if (recommendations == null || recommendations.isEmpty()) {
            return;
        }

        try {
            // Build context once for all calls
            String context = buildPortfolioContext(recommendations, userCards);
            String langInstruction = getLanguageInstruction(locale);

            // Create parallel API calls for each category
            List<CompletableFuture<Void>> futures = new ArrayList<>();

            for (CategoryRecommendation rec : recommendations) {
                CompletableFuture<Void> future = CompletableFuture.runAsync(() -> {
                    try {
                        String prompt = buildIndividualPrompt(rec, userCards, context, langInstruction);
                        String response = callOpenAiApi(prompt);
                        if (response != null && !response.isEmpty()) {
                            rec.setAiExplanation(response.trim());
                        }
                    } catch (Exception e) {
                        log.warn("Failed to generate AI explanation for {}: {}",
                            rec.getCategory(), e.getMessage());
                    }
                }, executor);
                futures.add(future);
            }

            // Wait for all to complete with timeout
            CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
                .get(15, TimeUnit.SECONDS);

        } catch (Exception e) {
            log.warn("Failed to generate AI explanations: {}", e.getMessage());
        }
    }

    /**
     * Build portfolio context summary (shared across all prompts)
     */
    private String buildPortfolioContext(List<CategoryRecommendation> recommendations,
                                         List<CreditCardDTO> userCards) {
        BigDecimal totalSpend = recommendations.stream()
            .map(CategoryRecommendation::getMonthlySpend)
            .reduce(BigDecimal.ZERO, BigDecimal::add);

        BigDecimal totalReward = recommendations.stream()
            .map(CategoryRecommendation::getMonthlyReward)
            .reduce(BigDecimal.ZERO, BigDecimal::add);

        StringBuilder cards = new StringBuilder();
        for (CreditCardDTO card : userCards) {
            cards.append(String.format("• %s %s (base %.1f%%)\n",
                card.getBank(), card.getName(),
                card.getBaseRewardRate() != null ? card.getBaseRewardRate().doubleValue() * 100 : 0));
        }

        return String.format("""
            Client Portfolio:
            %s
            Total Monthly Spend: $%.0f
            Total Monthly Cashback: $%.2f (effective rate: %.2f%%)
            """,
            cards.toString(),
            totalSpend.doubleValue(),
            totalReward.doubleValue(),
            totalSpend.compareTo(BigDecimal.ZERO) > 0
                ? totalReward.divide(totalSpend, 4, RoundingMode.HALF_UP).multiply(BigDecimal.valueOf(100)).doubleValue()
                : 0
        );
    }

    /**
     * Build prompt for individual category - focused, professional advisor style
     */
    private String buildIndividualPrompt(CategoryRecommendation rec,
                                         List<CreditCardDTO> userCards,
                                         String context,
                                         String langInstruction) {
        CreditCardDTO bestCard = rec.getRecommendedCard();

        // Build comparison with alternatives
        StringBuilder alternatives = new StringBuilder();
        for (CreditCardDTO card : userCards) {
            if (!card.getId().equals(bestCard.getId())) {
                BigDecimal cardRate = getCardRateForCategory(card, rec.getCategory());
                BigDecimal wouldEarn = rec.getMonthlySpend().multiply(cardRate).setScale(2, RoundingMode.HALF_UP);
                BigDecimal diff = rec.getMonthlyReward().subtract(wouldEarn);
                alternatives.append(String.format("  • %s %s: %.1f%% → $%.2f/mo (差额: $%.2f)\n",
                    card.getBank(), card.getName(),
                    cardRate.doubleValue() * 100,
                    wouldEarn.doubleValue(),
                    diff.doubleValue()));
            }
        }

        String categoryName = rec.getCategory().getDisplayName();

        return String.format("""
            %s

            You are a senior financial advisor at a private wealth management firm. A client has asked for your professional opinion on their credit card strategy.

            %s

            CURRENT ANALYSIS - %s:
            • Monthly spend: $%.0f
            • Recommended card: %s %s
            • Reward rate: %.1f%%
            • Monthly cashback: $%.2f

            Alternative cards in portfolio:
            %s

            As their advisor, provide ONE concise insight (2-3 sentences max) about this specific category. Your insight should:

            1. Be data-driven - reference their actual numbers
            2. Provide genuine value - explain WHY this matters or reveal something non-obvious
            3. Sound like a real advisor - professional but personable, not robotic
            4. Be specific to THIS category - consider merchant coding quirks, seasonal patterns, or optimization opportunities unique to %s spending

            Do NOT:
            - Simply restate the recommendation
            - Give generic advice that applies to any card
            - Use filler phrases like "Great choice!" or "Smart move!"

            Respond with ONLY the insight, no labels or prefixes.
            """,
            langInstruction,
            context,
            categoryName,
            rec.getMonthlySpend().doubleValue(),
            bestCard.getBank(),
            bestCard.getName(),
            rec.getRewardRate().doubleValue() * 100,
            rec.getMonthlyReward().doubleValue(),
            alternatives.length() > 0 ? alternatives.toString() : "  (No alternatives in portfolio)",
            categoryName
        );
    }

    /**
     * Get card reward rate for a specific category
     */
    private BigDecimal getCardRateForCategory(CreditCardDTO card, SpendingCategory category) {
        if (card.getRewardRules() != null) {
            for (var rule : card.getRewardRules()) {
                if (rule.getCategory() == category) {
                    return rule.getRewardRate();
                }
            }
        }
        return card.getBaseRewardRate() != null ? card.getBaseRewardRate() : BigDecimal.ZERO;
    }

    /**
     * Get language instruction based on locale
     */
    private String getLanguageInstruction(String locale) {
        if (locale == null) locale = "en";

        return switch (locale.toLowerCase()) {
            case "zh", "zh-cn", "zh-tw" -> "IMPORTANT: Respond in Simplified Chinese. 用专业但易懂的语气，像资深理财顾问给客户的建议。";
            case "ja" -> "IMPORTANT: Respond in Japanese. プロフェッショナルで分かりやすいアドバイスを。";
            case "ko" -> "IMPORTANT: Respond in Korean. 전문적이고 이해하기 쉬운 조언을 해주세요.";
            case "fr" -> "IMPORTANT: Respond in French. Conseil professionnel mais accessible.";
            case "es" -> "IMPORTANT: Respond in Spanish. Consejo profesional pero accesible.";
            default -> ""; // English is default, no need for instruction
        };
    }

    /**
     * Call OpenAI API with optimized settings for concise responses
     */
    private String callOpenAiApi(String prompt) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.setBearerAuth(apiKey);

            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("model", model);
            requestBody.put("max_tokens", 150);
            requestBody.put("temperature", 0.8);
            requestBody.put("messages", List.of(
                Map.of("role", "system", "content",
                    "You are a senior financial advisor. Be concise, insightful, and data-driven. Never use filler phrases."),
                Map.of("role", "user", "content", prompt)
            ));

            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            ResponseEntity<String> response = restTemplate.exchange(
                baseUrl + "/v1/chat/completions",
                HttpMethod.POST,
                entity,
                String.class
            );

            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                JsonNode root = objectMapper.readTree(response.getBody());
                JsonNode choices = root.path("choices");
                if (choices.isArray() && choices.size() > 0) {
                    return choices.get(0).path("message").path("content").asText();
                }
            }

            log.warn("Unexpected OpenAI API response: {}", response.getBody());
            return null;

        } catch (Exception e) {
            log.error("OpenAI API call failed: {}", e.getMessage());
            return null;
        }
    }
}
